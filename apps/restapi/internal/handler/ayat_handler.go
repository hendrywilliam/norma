package handler

import (
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/model"
	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/service"
	"github.com/hendrywilliam/norma/apps/restapi/pkg/response"
)

type AyatHandler struct {
	service service.AyatService
}

func NewAyatHandler(service service.AyatService) *AyatHandler {
	return &AyatHandler{service: service}
}

func (h *AyatHandler) GetByID(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		response.BadRequest(c, "Invalid ID", err)
		return
	}

	ayat, err := h.service.GetByID(c.Request.Context(), id)
	if err != nil {
		response.InternalError(c, "Failed to get ayat", err)
		return
	}

	if ayat == nil {
		response.NotFound(c, "Ayat not found")
		return
	}

	response.OK(c, ayat)
}

func (h *AyatHandler) GetList(c *gin.Context) {
	pasalID, err := strconv.Atoi(c.Param("pasal_id"))
	if err != nil {
		response.BadRequest(c, "Invalid pasal_id", err)
		return
	}

	skip, _ := strconv.Atoi(c.DefaultQuery("skip", "0"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "50"))

	filter := &model.AyatFilter{
		PasalID: pasalID,
		Skip:    skip,
		Limit:   limit,
	}

	result, err := h.service.GetList(c.Request.Context(), filter)
	if err != nil {
		response.InternalError(c, "Failed to get ayat list", err)
		return
	}

	response.ListResponse(c, result.Items, response.MetaResponse{
		Total: result.Total,
		Skip:  result.Skip,
		Limit: result.Limit,
	})
}

func (h *AyatHandler) RegisterRoutes(r *gin.RouterGroup) {
	// Use :id for peraturan, :pasal_id for pasal to match the routes
	ayat := r.Group("/peraturan/:id/pasal/:pasal_id/ayat")
	{
		ayat.GET("", h.GetList)
		ayat.GET("/:id", h.GetByID)
	}
}
