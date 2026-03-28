package handler

import (
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/model"
	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/service"
	"github.com/hendrywilliam/norma/apps/restapi/pkg/response"
)

type PasalHandler struct {
	service service.PasalService
}

func NewPasalHandler(service service.PasalService) *PasalHandler {
	return &PasalHandler{service: service}
}

func (h *PasalHandler) GetByID(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		response.BadRequest(c, "Invalid ID", err)
		return
	}

	pasal, err := h.service.GetByID(c.Request.Context(), id)
	if err != nil {
		response.InternalError(c, "Failed to get pasal", err)
		return
	}

	if pasal == nil {
		response.NotFound(c, "Pasal not found")
		return
	}

	response.OK(c, pasal)
}

func (h *PasalHandler) GetList(c *gin.Context) {
	peraturanID := c.Param("id") // Use :id to match peraturan routes
	skip, _ := strconv.Atoi(c.DefaultQuery("skip", "0"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "50"))

	filter := &model.PasalFilter{
		PeraturanID: peraturanID,
		Skip:        skip,
		Limit:       limit,
	}

	result, err := h.service.GetList(c.Request.Context(), filter)
	if err != nil {
		response.InternalError(c, "Failed to get pasal list", err)
		return
	}

	response.ListResponse(c, result.Items, response.MetaResponse{
		Total: result.Total,
		Skip:  result.Skip,
		Limit: result.Limit,
	})
}

func (h *PasalHandler) RegisterRoutes(r *gin.RouterGroup) {
	pasal := r.Group("/peraturan/:id/pasal")
	{
		pasal.GET("", h.GetList)
		pasal.GET("/:pasal_id", h.GetByID)
	}
}
