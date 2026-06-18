import os
import json
import requests
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from langchain_core.language_models.llms import LLM
from langchain_core.prompts import PromptTemplate
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
import logging
import sys
from prometheus_fastapi_instrumentator import Instrumentator

# Environment configuration: pick the upstream provider based on env.
#
# If LOGOS_API_KEY is set we point at the TUM Logos endpoint and default
# to the openai/gpt-oss-120b model. Otherwise we default to LM Studio
# running on the host (host.docker.internal:1234 from inside Docker on
# macOS/Windows) with gemma-4-e2b. Either profile can still be
# overridden explicitly by setting LLM_API_URL / LLM_MODEL.
LOGOS_API_KEY = os.getenv("LOGOS_API_KEY")
if LOGOS_API_KEY:
    API_URL = "https://logos.aet.cit.tum.de/v1/chat/completions"
    MODEL_NAME = "openai/gpt-oss-120b"
    LLM_API_KEY = LOGOS_API_KEY
else:
    API_URL = os.getenv("LLM_API_URL", "http://localhost:1234/v1/chat/completions")
    MODEL_NAME = os.getenv("LLM_MODEL", "google/gemma-4-e2b")
    LLM_API_KEY = os.getenv("LLM_API_KEY") or os.getenv("CHAIR_API_KEY")

# Create FastAPI application instance
app = FastAPI(
    title="LLM Recommendation Service",
    description="Service that generates personalized food recommendations using an LLM",
    version="1.0.0"
)
Instrumentator().instrument(app).expose(app)

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

# Configure root logger for JSON output
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JsonFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])
# ...rest of your code...

class RecommendRequest(BaseModel):
    """
    Request schema for recommendation endpoint.

    Attributes:
        favorite_menu (List[str]): User's favorite meal names
        todays_menu (List[str]): Today's available meal names
    """
    favorite_menu: List[str] = Field(..., description="User's favorite meal names")
    todays_menu: List[str] = Field(..., description="Today's available meal names")


class RecommendResponse(BaseModel):
    """
    Response schema for recommendation endpoint.

    Attributes:
        recommendation (str): The personalized recommendation string.
    """
    recommendation: str = Field(..., description="Personalized food recommendation")


class OpenAICompatibleLLM(LLM):
    """LangChain LLM wrapper for any OpenAI-compatible /v1/chat/completions endpoint."""

    api_url: str = API_URL
    api_key: Optional[str] = LLM_API_KEY
    model_name: str = MODEL_NAME

    @property
    def _llm_type(self) -> str:
        return "openai_compatible"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        Call the OpenAI-compatible API to generate a response.

        Args:
            prompt: The input prompt to send to the model
            stop: Optional list of stop sequences
            run_manager: Optional callback manager for LangChain
            **kwargs: Additional keyword arguments

        Returns:
            The generated response text

        Raises:
            Exception: If API call fails
        """
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        # Build messages for chat completion
        messages = [
            {"role": "user", "content": prompt}
        ]

        payload = {
            "model": self.model_name,
            "messages": messages,
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract the response content
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                return content.strip()
            else:
                raise ValueError("Unexpected response format from API")
                
        except requests.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
        except (KeyError, IndexError, ValueError) as e:
            raise Exception(f"Failed to parse API response: {str(e)}")


# Initialize the LLM
llm = OpenAICompatibleLLM()

# Create the prompt template
recommendation_prompt = PromptTemplate(
    input_variables=["favorite_menu", "todays_menu"],
    template="""You are a helpful food recommendation assistant. Your task is to suggest exactly one dish from today's menu based on the user's preferences.

User's favorite meals: {favorite_menu}

Today's available meals: {todays_menu}

Based on the user's favorite meals, please recommend exactly ONE meal from today's available options. 
Consider:
- Similarity to the user's favorite meals
- Flavor profiles that match their preferences
- Availability in today's menu

IMPORTANT: You must respond with ONLY the exact name of one dish from today's menu. Do not include any explanations, additional text, punctuation, or formatting. Just return the dish name exactly as it appears in today's menu.

Example format: Spaghetti Carbonara

Recommendation:"""
)

# Create the chain using the new RunnableSequence pattern
recommendation_chain = recommendation_prompt | llm

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "LLM Recommendation Service"}


@app.post(
    "/recommend",
    response_model=RecommendResponse,
    summary="Generate personalized food recommendation",
    description="Accepts user's favorite meals and today's menu, returns a personalized meal recommendation via an OpenAI-compatible LLM (e.g. LM Studio)."
)
async def recommend(req: RecommendRequest) -> RecommendResponse:
    """
    Generate a personalized food recommendation using LangChain against an OpenAI-compatible LLM endpoint.
    
    Args:
        req: Request containing user's favorite meals and today's menu
        
    Returns:
        RecommendResponse containing the recommendation
        
    Raises:
        HTTPException: If the API call fails or other errors occur
    """
    try:
        if not req.favorite_menu:
            raise HTTPException(
                status_code=400, 
                detail="favorite_menu cannot be empty"
            )
        
        if not req.todays_menu:
            raise HTTPException(
                status_code=400, 
                detail="todays_menu cannot be empty"
            )
        
        # Format arrays as comma-separated strings for better processing
        favorite_meals_str = ", ".join(req.favorite_menu)
        todays_meals_str = ", ".join(req.todays_menu)
        
        # Use LangChain to generate recommendation
        recommendation = recommendation_chain.invoke({
            "favorite_menu": favorite_meals_str,
            "todays_menu": todays_meals_str
        })
        
        # Return the LLM response as the recommendation
        return RecommendResponse(recommendation=recommendation)
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log the error (in production, use proper logging)
        print(f"Error generating recommendation: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate recommendation: {str(e)}"
        )


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "LLM Recommendation Service",
        "version": "1.0.0",
        "description": "Generates personalized food recommendations using LangChain against an OpenAI-compatible LLM endpoint (e.g. LM Studio).",
        "endpoints": {
            "health": "/health",
            "recommend": "/recommend",
            "docs": "/docs"
        }
    }

# Entry point for direct execution
if __name__ == "__main__":
    """
    Entry point for `python main.py` invocation.
    Starts Uvicorn server serving this FastAPI app.

    Honors PORT environment variable (default: 5001).
    Reload=True enables live-reload during development.
    """
    import uvicorn

    port = int(os.getenv("PORT", 5001))
    
    print(f"Starting LLM Recommendation Service on port {port}")
    print(f"API Documentation available at: http://localhost:{port}/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
