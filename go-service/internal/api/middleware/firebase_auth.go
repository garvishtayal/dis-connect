package middleware

import (
	"fmt"
	"net/http"
	"strings"

	firebaseauth "firebase.google.com/go/v4/auth"
	"github.com/gin-gonic/gin"

	"github.com/garvishtayal/dis-connect/go-service/internal/auth"
)

const (
	ContextFirebaseUID      = "firebase_uid"
	ContextFirebaseEmail    = "firebase_email"
	ContextFirebaseProvider = "firebase_provider"
	ContextFirebaseClaims   = "firebase_claims"
)

// FirebaseAuth validates Firebase ID tokens for protected routes.
func FirebaseAuth(validator *auth.TokenValidator) gin.HandlerFunc {
	return func(c *gin.Context) {
		if validator == nil {
			c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{"error": "auth validator not configured"})
			return
		}

		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "missing authorization header"})
			return
		}

		if !strings.HasPrefix(authHeader, "Bearer ") {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "invalid authorization header"})
			return
		}

		token := strings.TrimPrefix(authHeader, "Bearer ")
		if token == "" {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "empty token"})
			return
		}

		verified, err := validator.VerifyIDToken(c.Request.Context(), token)
		if err != nil {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "invalid firebase token"})
			return
		}

		c.Set(ContextFirebaseUID, verified.UID)
		c.Set(ContextFirebaseEmail, extractEmail(verified))
		c.Set(ContextFirebaseProvider, extractSignInProvider(verified))
		c.Set(ContextFirebaseClaims, verified.Claims)

		c.Next()
	}
}

// extractEmail returns email from token claims when present.
func extractEmail(token *firebaseauth.Token) string {
	email, _ := token.Claims["email"].(string)
	return email
}

// extractSignInProvider returns Firebase sign_in_provider from claims.
func extractSignInProvider(token *firebaseauth.Token) string {
	firebaseClaim, ok := token.Claims["firebase"].(map[string]any)
	if !ok {
		return ""
	}
	provider, _ := firebaseClaim["sign_in_provider"].(string)
	return provider
}

// RequireFirebaseUID gets firebase UID from Gin context.
func RequireFirebaseUID(c *gin.Context) (string, error) {
	uid, ok := c.Get(ContextFirebaseUID)
	if !ok {
		return "", fmt.Errorf("firebase uid missing in context")
	}
	value, ok := uid.(string)
	if !ok || value == "" {
		return "", fmt.Errorf("firebase uid has invalid type")
	}
	return value, nil
}
