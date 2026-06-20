package org.librime.libribackend.Security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import jakarta.annotation.PostConstruct;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.nio.charset.StandardCharsets;
import java.security.Key;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Function;

@Component
public class JwtUtil {

    @Value("${jwt.secret}")
    private String secret;

    @Value("${jwt.expiration}")
    private long expiration;

    private static final Logger log = LoggerFactory.getLogger(JwtUtil.class);

    @Value("${google.project.id:}")
    private String googleProjectId;

    private Key key;
    private final Map<String, java.security.PublicKey> googlePublicKeys = new java.util.concurrent.ConcurrentHashMap<>();
    private long keysLastFetched = 0;

    @PostConstruct
    public void init() {
        this.key = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
    }

    public String generateToken(String userId) {
        Map<String, Object> claims = new HashMap<>();
        return createToken(claims, userId);
    }

    private String createToken(Map<String, Object> claims, String subject) {
        return Jwts.builder()
                .setClaims(claims)
                .setSubject(subject)
                .setIssuedAt(new Date(System.currentTimeMillis()))
                .setExpiration(new Date(System.currentTimeMillis() + expiration))
                .signWith(key)
                .compact();
    }

    public String extractUserId(String token) {
        return extractClaim(token, Claims::getSubject);
    }

    public <T> T extractClaim(String token, Function<Claims, T> claimsResolver) {
        final Claims claims = extractAllClaims(token);
        return claimsResolver.apply(claims);
    }

    private Claims extractAllClaims(String token) {
        return Jwts.parserBuilder().setSigningKey(key).build().parseClaimsJws(token).getBody();
    }

    public Boolean validateToken(String token) {
        try {
            Jwts.parserBuilder().setSigningKey(key).build().parseClaimsJws(token);
            return !isTokenExpired(token);
        } catch (Exception e) {
            return false;
        }
    }

    private Boolean isTokenExpired(String token) {
        return extractExpiration(token).before(new Date());
    }

    public Date extractExpiration(String token) {
        return extractClaim(token, Claims::getExpiration);
    }

    // --- Google OAuth support (Identity Platform) ---

    private String getKidFromToken(String token) {
        try {
            int firstDot = token.indexOf('.');
            if (firstDot == -1) return null;
            String headerJson = new String(java.util.Base64.getUrlDecoder().decode(token.substring(0, firstDot)), StandardCharsets.UTF_8);
            com.fasterxml.jackson.databind.ObjectMapper mapper = new com.fasterxml.jackson.databind.ObjectMapper();
            com.fasterxml.jackson.databind.JsonNode node = mapper.readTree(headerJson);
            return node.has("kid") ? node.get("kid").asText() : null;
        } catch (Exception e) {
            return null;
        }
    }

    private synchronized void refreshGooglePublicKeys() {
        long now = System.currentTimeMillis();
        if (now - keysLastFetched < 60000 && !googlePublicKeys.isEmpty()) {
            return;
        }
        try {
            java.net.http.HttpClient client = java.net.http.HttpClient.newHttpClient();
            java.net.http.HttpRequest request = java.net.http.HttpRequest.newBuilder()
                    .uri(java.net.URI.create("https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"))
                    .GET()
                    .build();
            java.net.http.HttpResponse<String> response = client.send(request, java.net.http.HttpResponse.BodyHandlers.ofString());
            if (response.statusCode() == 200) {
                com.fasterxml.jackson.databind.ObjectMapper mapper = new com.fasterxml.jackson.databind.ObjectMapper();
                Map<String, String> certs = mapper.readValue(response.body(), new com.fasterxml.jackson.core.type.TypeReference<Map<String, String>>() {});
                java.security.cert.CertificateFactory cf = java.security.cert.CertificateFactory.getInstance("X.509");
                Map<String, java.security.PublicKey> newKeys = new HashMap<>();
                for (Map.Entry<String, String> entry : certs.entrySet()) {
                    try {
                        java.io.ByteArrayInputStream in = new java.io.ByteArrayInputStream(entry.getValue().getBytes(StandardCharsets.UTF_8));
                        java.security.cert.X509Certificate cert = (java.security.cert.X509Certificate) cf.generateCertificate(in);
                        newKeys.put(entry.getKey(), cert.getPublicKey());
                    } catch (Exception e) {
                        log.error("Failed to parse certificate for kid {}: {}", entry.getKey(), e.getMessage());
                    }
                }
                if (!newKeys.isEmpty()) {
                    googlePublicKeys.clear();
                    googlePublicKeys.putAll(newKeys);
                    keysLastFetched = now;
                }
            }
        } catch (Exception e) {
            log.error("Failed to fetch Google public keys: {}", e.getMessage());
        }
    }

    private java.security.PublicKey getGooglePublicKey(String kid) {
        java.security.PublicKey key = googlePublicKeys.get(kid);
        if (key == null) {
            refreshGooglePublicKeys();
            key = googlePublicKeys.get(kid);
        }
        return key;
    }

    public Boolean validateGoogleToken(String token) {
        try {
            if (googleProjectId == null || googleProjectId.trim().isEmpty()) {
                return false;
            }
            String kid = getKidFromToken(token);
            if (kid == null) {
                return false;
            }
            java.security.PublicKey publicKey = getGooglePublicKey(kid);
            if (publicKey == null) {
                return false;
            }
            Claims claims = Jwts.parserBuilder()
                    .setSigningKey(publicKey)
                    .build()
                    .parseClaimsJws(token)
                    .getBody();

            String expectedIssuer = "https://securetoken.google.com/" + googleProjectId;
            return expectedIssuer.equals(claims.getIssuer()) &&
                   googleProjectId.equals(claims.getAudience()) &&
                   claims.getExpiration().after(new Date());
        } catch (Exception e) {
            log.error("Failed to validate Google token: {}", e.getMessage());
            return false;
        }
    }

    public String extractGoogleUserId(String token) {
        try {
            if (googleProjectId == null || googleProjectId.trim().isEmpty()) {
                return null;
            }
            String kid = getKidFromToken(token);
            if (kid == null) {
                return null;
            }
            java.security.PublicKey publicKey = getGooglePublicKey(kid);
            if (publicKey == null) {
                return null;
            }
            Claims claims = Jwts.parserBuilder()
                    .setSigningKey(publicKey)
                    .build()
                    .parseClaimsJws(token)
                    .getBody();
            return claims.getSubject();
        } catch (Exception e) {
            return null;
        }
    }
}
