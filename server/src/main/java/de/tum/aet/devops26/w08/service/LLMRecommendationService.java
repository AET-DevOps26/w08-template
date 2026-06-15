package de.tum.aet.devops26.w08.service;

import de.tum.aet.devops26.w08.client.LLMRestClient;
import de.tum.aet.devops26.w08.dto.Dish;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class LLMRecommendationService {

    private final LLMRestClient llmRestClient;
    private final Counter recommendationRequestCounter;
    private final Counter recommendationErrorCounter;
    private final Timer recommendationTimer;

    public LLMRecommendationService(LLMRestClient llmRestClient, MeterRegistry registry) {
        this.llmRestClient = llmRestClient;
        
        // Initialize metrics
        this.recommendationRequestCounter = Counter.builder("recommendation_service.requests.total")
                .description("Total number of recommendation requests")
                .register(registry);
                
        this.recommendationErrorCounter = Counter.builder("recommendation_service.errors.total")
                .description("Number of errors when getting recommendations")
                .register(registry);
                
        this.recommendationTimer = Timer.builder("recommendation_service.request.duration")
                .description("Time taken to get recommendations")
                .register(registry);
    }

    /**
     * Get recommendation from LLM service using REST API
     * @param favoriteMeals list of user's favorite meal names
     * @param todayMeals list of today's available dishes
     * @return recommendation as a string
     */
    public String getRecommendationFromLLM(List<String> favoriteMeals, List<Dish> todayMeals) {
        recommendationRequestCounter.increment();
        
        return recommendationTimer.record(() -> {
            try {
                // Convert today's dishes to meal names
                List<String> todayMealNames = todayMeals.stream()
                        .map(Dish::name)
                        .collect(Collectors.toList());

                return llmRestClient.generateRecommendations(favoriteMeals, todayMealNames);

            } catch (Exception e) {
                System.err.println("Error fetching recommendation from LLM service: " + e.getMessage());
                recommendationErrorCounter.increment();
                return "";
            }
        });
    }

}
