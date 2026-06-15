package de.tum.aet.devops26.w08;

import de.tum.aet.devops26.w08.entity.UserPreferences;
import org.springframework.data.jpa.repository.JpaRepository;

/*
    Required for interacting with the database.
    A Spring Data JPA interface that provides ready-to-use database operations.
 */

public interface UserPreferenceRepository extends JpaRepository<UserPreferences, String> {

}
