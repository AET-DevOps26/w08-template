package de.tum.aet.devops26.w08.service;

import de.tum.aet.devops26.w08.dto.Day;
import de.tum.aet.devops26.w08.dto.Dish;
import de.tum.aet.devops26.w08.dto.Week;
import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;
import io.micrometer.core.instrument.Timer;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.time.Clock;
import java.time.LocalDate;
import java.time.temporal.WeekFields;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.concurrent.TimeUnit;

@Service
public class CanteenService {

    private final RestClient restClient;
    private final Clock clock;
    private final Counter mealRequestCounter;
    private final Counter mealFoundCounter;
    private final Counter mealErrorCounter;
    private final Timer mealRequestTimer;

    public CanteenService(RestClient.Builder builder, Clock clock, MeterRegistry registry,
                          @Value("${canteen.api.base-url:https://tum-dev.github.io/eat-api/}") String baseUrl) {
        this.restClient = builder.baseUrl(baseUrl).build();
        this.clock = clock;
        
        // Initialize metrics
        this.mealRequestCounter = Counter.builder("meal_service.requests.total")
                .description("Total number of meal requests")
                .register(registry);
        
        this.mealFoundCounter = Counter.builder("meal_service.meals.found")
                .description("Number of meals found")
                .register(registry);
        
        this.mealErrorCounter = Counter.builder("meal_service.errors.total")
                .description("Number of errors when fetching meals")
                .register(registry);
        
        this.mealRequestTimer = Timer.builder("meal_service.request.duration")
                .description("Time taken to fetch meals")
                .register(registry);
    }

    /**
     * Get today's meals for a specific canteen
     * @param canteenName the name of the canteen, e.g., "mensa-garching"
     * @return list of dishes available today, or empty list if no data found
     */
    public List<Dish> getTodayMeals(String canteenName) {
        mealRequestCounter.increment();
        
        return mealRequestTimer.record(() -> {
            LocalDate today = LocalDate.now(clock);
            int year = today.getYear();
            int weekNumber = today.get(WeekFields.of(Locale.getDefault()).weekOfWeekBasedYear());
            String weekStr = String.format("%02d", weekNumber);
            
            try {
                Week week = restClient.get()
                        .uri(canteenName + "/" + year + "/" + weekStr + ".json")
                        .retrieve()
                        .body(Week.class);
                
                if (week != null && week.days() != null) {
                    Optional<Day> todayMenu = week.days().stream()
                            .filter(day -> day.date().equals(today))
                            .findFirst();
                    
                    List<Dish> dishes = todayMenu.map(Day::dishes).orElse(List.of());
                    
                    // Record metrics
                    if (!dishes.isEmpty()) {
                        mealFoundCounter.increment(dishes.size());
                    }
                    
                    return dishes;
                }
            } catch (Exception e) {
                // Log the exception and record metric
                System.err.println("Error fetching meals: " + e.getMessage());
                mealErrorCounter.increment();
            }
            
            return List.of();
        });
    }
}