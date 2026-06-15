package de.tum.aet.devops26.w08.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

public record RecommendRequest(
    @JsonProperty("favorite_menu") List<String> favoriteMenu,
    @JsonProperty("todays_menu") List<String> todaysMenu
) {}
