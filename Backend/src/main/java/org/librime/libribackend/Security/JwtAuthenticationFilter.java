package org.librime.libribackend.Security;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.librime.libribackend.DB.Repository.JobRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseCookie;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.ArrayList;
import java.util.UUID;

@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private static final Logger log = LoggerFactory.getLogger(JwtAuthenticationFilter.class);

    @Autowired
    private JwtUtil jwtUtil;

    @Autowired
    private JobRepository jobRepository;

    private static final String COOKIE_NAME = "libriME_jwt";

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {

        if (request.getMethod().equalsIgnoreCase("OPTIONS")) {
            filterChain.doFilter(request, response);
            return;
        }

        String path = request.getServletPath();
        if (path.equals("/health") || path.startsWith("/v3/api-docs") || path.startsWith("/swagger-ui")) {
            filterChain.doFilter(request, response);
            return;
        }

        if (request.getMethod().equals("PUT") && path.startsWith("/jobs/")) {
            filterChain.doFilter(request, response);
            return;
        }

        String authHeader = request.getHeader("Authorization");
        String authenticatedUserId = null;
        boolean isGoogleAuth = false;

        // 1. Try to extract and validate Google OAuth Token or fallback to validating local JWT in the Authorization header
        if (authHeader != null && authHeader.startsWith("Bearer ")) {
            String jwt = authHeader.substring(7);
            if (jwtUtil.validateGoogleToken(jwt)) {
                authenticatedUserId = jwtUtil.extractGoogleUserId(jwt);
                isGoogleAuth = true;
            } else if (jwtUtil.validateToken(jwt)) {
                authenticatedUserId = jwtUtil.extractUserId(jwt);
            }
        }

        // 2. Read the anonymous session cookie if it exists
        String anonymousJwt = null;
        String anonymousUserId = null;
        if (request.getCookies() != null) {
            for (Cookie cookie : request.getCookies()) {
                if (COOKIE_NAME.equals(cookie.getName())) {
                    anonymousJwt = cookie.getValue();
                    try {
                        if (jwtUtil.validateToken(anonymousJwt)) {
                            anonymousUserId = jwtUtil.extractUserId(anonymousJwt);
                        }
                    } catch (Exception e) {
                        // Ignore invalid cookie
                    }
                    break;
                }
            }
        }

        // 3. Migrate jobs from anonymous session to Google account
        if (isGoogleAuth && anonymousUserId != null) {
            try {
                int migratedCount = jobRepository.migrateJobs(anonymousUserId, authenticatedUserId);
                log.info("Migrated {} jobs from anonymous user {} to authenticated user {}", 
                        migratedCount, anonymousUserId, authenticatedUserId);
            } catch (Exception e) {
                log.error("Failed to migrate jobs from anonymous user {} to authenticated user {}: {}", 
                        anonymousUserId, authenticatedUserId, e.getMessage());
            }

            // Clear the anonymous cookie using ResponseCookie with SameSite=None
            ResponseCookie deleteCookie = ResponseCookie.from(COOKIE_NAME, "")
                    .path("/")
                    .httpOnly(true)
                    .maxAge(0)
                    .secure(true)
                    .sameSite("None")
                    .build();
            response.addHeader(HttpHeaders.SET_COOKIE, deleteCookie.toString());
        }

        // 4. Fallback to existing local anonymous session logic if not logged in via Google
        if (authenticatedUserId == null) {
            if (anonymousUserId != null) {
                authenticatedUserId = anonymousUserId;
            } else {
                // Generate a new anonymous user session and set ResponseCookie with SameSite=None
                authenticatedUserId = UUID.randomUUID().toString();
                String newLocalJwt = jwtUtil.generateToken(authenticatedUserId);
                ResponseCookie cookie = ResponseCookie.from(COOKIE_NAME, newLocalJwt)
                        .httpOnly(true)
                        .secure(true)
                        .path("/")
                        .maxAge(60 * 60 * 24 * 30) // 30 days
                        .sameSite("None")
                        .build();
                response.addHeader(HttpHeaders.SET_COOKIE, cookie.toString());
            }
        }

        if (SecurityContextHolder.getContext().getAuthentication() == null) {
            UsernamePasswordAuthenticationToken authenticationToken = new UsernamePasswordAuthenticationToken(
                    authenticatedUserId, null, new ArrayList<>());
            authenticationToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
            SecurityContextHolder.getContext().setAuthentication(authenticationToken);
        }

        filterChain.doFilter(request, response);
    }
}
