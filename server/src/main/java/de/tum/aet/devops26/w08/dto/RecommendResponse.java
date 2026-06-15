package de.tum.aet.devops26.w08.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public record RecommendResponse(
    @JsonProperty("recommendation") String recommendation
) {}
