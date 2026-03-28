package handler

import (
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/model"
	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/service"
	"github.com/hendrywilliam/norma/apps/restapi/pkg/response"
)

type BabHandler struct {
	service service.BabService
}

func NewBabHandler(service service.BabService) *BabHandler {
	return &BabHandler{service: service}
}

func (h *BabHandler) GetByID(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		response.BadRequest(c, "Invalid ID", err)
		return
	}

	bab, err := h.service.GetByID(c.Request.Context(), id)
	if err != nil {
		response.InternalError(c, "Failed to get bab", err)
		return
	}

	if bab == nil {
		response.NotFound(c, "Bab not found")
		return
	}

	response.OK(c, bab)
}

func (h *BabHandler) GetList(c *gin.Context) {
	peraturanID := c.Param("id") // Use :id to match peraturan routes
	skip, _ := strconv.Atoi(c.DefaultQuery("skip", "0"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "50"))

	filter := &model.BabFilter{
		PeraturanID: peraturanID,
		Skip:        skip,
		Limit:       limit,
	}

	result, err := h.service.GetList(c.Request.Context(), filter)
	if err != nil {
		response.InternalError(c, "Failed to get bab list", err)
		return
	}

	response.ListResponse(c, result.Items, response.MetaResponse{
		Total: result.Total,
		Skip:  result.Skip,
		Limit: result.Limit,
	})
}

func (h *BabHandler) RegisterRoutes(r *gin.RouterGroup) {
	bab := r.Group("/peraturan/:id/bab")
	{
		bab.GET("", h.GetList)
		bab.GET("/:id", h.GetByID)
	}
}
