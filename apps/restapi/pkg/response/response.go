package response

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

type Response struct {
	Success bool        `json:"success"`
	Message string      `json:"message"`
	Data    interface{} `json:"data,omitempty"`
	Error   string      `json:"error,omitempty"`
}

type MetaResponse struct {
	Total int `json:"total"`
	Skip  int `json:"skip"`
	Limit int `json:"limit"`
}

func Success(c *gin.Context, statusCode int, message string, data interface{}) {
	c.JSON(statusCode, Response{
		Success: true,
		Message: message,
		Data:    data,
	})
}

func Created(c *gin.Context, message string, data interface{}) {
	Success(c, http.StatusCreated, message, data)
}

func OK(c *gin.Context, data interface{}) {
	Success(c, http.StatusOK, "Success", data)
}

func Error(c *gin.Context, statusCode int, message string, err error) {
	errorMsg := ""
	if err != nil {
		errorMsg = err.Error()
	}
	c.JSON(statusCode, Response{
		Success: false,
		Message: message,
		Error:   errorMsg,
	})
}

func BadRequest(c *gin.Context, message string, err error) {
	Error(c, http.StatusBadRequest, message, err)
}

func NotFound(c *gin.Context, message string) {
	Error(c, http.StatusNotFound, message, nil)
}

func InternalError(c *gin.Context, message string, err error) {
	Error(c, http.StatusInternalServerError, message, err)
}

func ListResponse(c *gin.Context, data interface{}, meta MetaResponse) {
	c.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "Success",
		"data":    data,
		"meta":    meta,
	})
}
