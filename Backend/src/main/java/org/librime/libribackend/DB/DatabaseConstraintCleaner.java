package org.librime.libribackend.DB;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class DatabaseConstraintCleaner implements CommandLineRunner {

    private static final Logger log = LoggerFactory.getLogger(DatabaseConstraintCleaner.class);

    private final JdbcTemplate jdbcTemplate;

    @Autowired
    public DatabaseConstraintCleaner(java.util.Optional<JdbcTemplate> jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate.orElse(null);
    }

    @Override
    public void run(String... args) throws Exception {
        if (jdbcTemplate == null) {
            log.info("JdbcTemplate not available, skipping check constraint cleanup.");
            return;
        }

        try {
            // Get the database product name to check if we are running on MySQL
            String databaseProductName = jdbcTemplate.getDataSource().getConnection().getMetaData().getDatabaseProductName();
            log.info("Database product name: {}", databaseProductName);

            if (databaseProductName.toLowerCase().contains("mysql")) {
                log.info("Running on MySQL. Cleaning up legacy check constraints on 'jobs' table...");
                
                String query = "SELECT CONSTRAINT_NAME FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS " +
                               "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'jobs' AND CONSTRAINT_TYPE = 'CHECK'";
                
                List<String> constraints = jdbcTemplate.queryForList(query, String.class);
                
                for (String constraint : constraints) {
                    try {
                        log.info("Dropping check constraint '{}' from 'jobs' table...", constraint);
                        jdbcTemplate.execute("ALTER TABLE jobs DROP CHECK " + constraint);
                        log.info("Successfully dropped check constraint '{}'", constraint);
                    } catch (Exception e) {
                        log.warn("Failed to drop check constraint '{}': {}", constraint, e.getMessage());
                    }
                }
            } else {
                log.info("Database is not MySQL. Skipping check constraint cleanup.");
            }
        } catch (Exception e) {
            log.warn("Could not clean up check constraints: {}", e.getMessage());
        }
    }
}
