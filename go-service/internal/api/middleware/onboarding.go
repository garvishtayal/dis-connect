package middleware

import (
	"net/http"

	"github.com/gin-gonic/gin"

	"github.com/garvishtayal/dis-connect/go-service/internal/repository/postgres"
)

// OnboardingRequired ensures user onboarding is completed before accessing gated routes.
func OnboardingRequired(userRepo *postgres.UserRepository) gin.HandlerFunc {
	return func(c *gin.Context) {
		if userRepo == nil {
			c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{"error": "user repository not configured"})
			return
		}

		firebaseUID, err := RequireFirebaseUID(c)
		if err != nil {
			c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "unauthorized"})
			return
		}

		completed, err := userRepo.IsOnboardingCompletedByFirebaseUID(c.Request.Context(), firebaseUID)
		if err != nil {
			c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{"error": "failed to verify onboarding status"})
			return
		}
		if !completed {
			c.AbortWithStatusJSON(http.StatusForbidden, gin.H{"error": "onboarding not completed"})
			return
		}

		c.Next()
	}
}
