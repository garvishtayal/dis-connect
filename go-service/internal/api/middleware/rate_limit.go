package middleware

import "github.com/gin-gonic/gin"

// RateLimit is a placeholder rate limiter.
func RateLimit() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Next()
	}
}

