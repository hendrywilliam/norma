package handler

import (
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/model"
	"github.com/hendrywilliam/norma/apps/restapi/internal/domain/service"
	"github.com/hendrywilliam/norma/apps/restapi/pkg/response"
)

type PeraturanHandler struct {
	service service.PeraturanService
}

func NewPeraturanHandler(service service.PeraturanService) *PeraturanHandler {
	return &PeraturanHandler{service: service}
}

type CreatePeraturanRequest struct {
	ID              string  `json:"id" binding:"required"`
	Judul           string  `json:"judul" binding:"required"`
	Nomor           string  `json:"nomor" binding:"required"`
	Tahun           int     `json:"tahun" binding:"required"`
	Kategori        string  `json:"kategori" binding:"required"`
	URL             string  `json:"url" binding:"required"`
	PDFURL          *string `json:"pdf_url"`
	JenisPeraturan  *string `json:"jenis_peraturan"`
	Pemrakarsa      *string `json:"pemrakarsa"`
	Tentang         *string `json:"tentang"`
	TempatPenetapan *string `json:"tempat_penetapan"`
	StatusPeraturan string  `json:"status_peraturan"`
	JumlahDilihat   int     `json:"jumlah_dilihat"`
	JumlahDownload  int     `json:"jumlah_download"`
}

func (h *PeraturanHandler) Create(c *gin.Context) {
	var req CreatePeraturanRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		response.BadRequest(c, "Invalid request body", err)
		return
	}

	peraturan := &model.Peraturan{
		ID:              req.ID,
		Judul:           req.Judul,
		Nomor:           req.Nomor,
		Tahun:           req.Tahun,
		Kategori:        req.Kategori,
		URL:             req.URL,
		PDFURL:          req.PDFURL,
		JenisPeraturan:  req.JenisPeraturan,
		Pemrakarsa:      req.Pemrakarsa,
		Tentang:         req.Tentang,
		TempatPenetapan: req.TempatPenetapan,
		StatusPeraturan: req.StatusPeraturan,
		JumlahDilihat:   req.JumlahDilihat,
		JumlahDownload:  req.JumlahDownload,
	}

	if err := h.service.Create(c.Request.Context(), peraturan); err != nil {
		response.InternalError(c, "Failed to create peraturan", err)
		return
	}

	response.Created(c, "Peraturan created successfully", peraturan)
}

func (h *PeraturanHandler) GetByID(c *gin.Context) {
	id := c.Param("id")

	peraturan, err := h.service.GetByID(c.Request.Context(), id)
	if err != nil {
		response.InternalError(c, "Failed to get peraturan", err)
		return
	}

	if peraturan == nil {
		response.NotFound(c, "Peraturan not found")
		return
	}

	response.OK(c, peraturan)
}

func (h *PeraturanHandler) GetList(c *gin.Context) {
	skip, _ := strconv.Atoi(c.DefaultQuery("skip", "0"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "20"))

	filter := &model.PeraturanFilter{
		Skip:  skip,
		Limit: limit,
	}

	if category := c.Query("category"); category != "" {
		filter.Category = &category
	}

	if year := c.Query("year"); year != "" {
		yearInt, err := strconv.Atoi(year)
		if err == nil {
			filter.Year = &yearInt
		}
	}

	if search := c.Query("search"); search != "" {
		filter.Search = &search
	}

	result, err := h.service.GetList(c.Request.Context(), filter)
	if err != nil {
		response.InternalError(c, "Failed to get peraturan list", err)
		return
	}

	response.ListResponse(c, result.Items, response.MetaResponse{
		Total: result.Total,
		Skip:  result.Skip,
		Limit: result.Limit,
	})
}

func (h *PeraturanHandler) Search(c *gin.Context) {
	query := c.Query("q")
	if query == "" {
		response.BadRequest(c, "Search query is required", nil)
		return
	}

	skip, _ := strconv.Atoi(c.DefaultQuery("skip", "0"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "20"))

	result, err := h.service.Search(c.Request.Context(), query, skip, limit)
	if err != nil {
		response.InternalError(c, "Failed to search peraturan", err)
		return
	}

	response.ListResponse(c, result.Items, response.MetaResponse{
		Total: result.Total,
		Skip:  result.Skip,
		Limit: result.Limit,
	})
}

func (h *PeraturanHandler) Update(c *gin.Context) {
	id := c.Param("id")

	var req CreatePeraturanRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		response.BadRequest(c, "Invalid request body", err)
		return
	}

	peraturan := &model.Peraturan{
		Judul:    req.Judul,
		Nomor:    req.Nomor,
		Tahun:    req.Tahun,
		Kategori: req.Kategori,
		URL:      req.URL,
	}

	if err := h.service.Update(c.Request.Context(), id, peraturan); err != nil {
		response.InternalError(c, "Failed to update peraturan", err)
		return
	}

	response.OK(c, gin.H{"message": "Peraturan updated successfully"})
}

func (h *PeraturanHandler) Delete(c *gin.Context) {
	id := c.Param("id")

	if err := h.service.Delete(c.Request.Context(), id); err != nil {
		response.InternalError(c, "Failed to delete peraturan", err)
		return
	}

	response.OK(c, gin.H{"message": "Peraturan deleted successfully"})
}

func (h *PeraturanHandler) RegisterRoutes(r *gin.RouterGroup) {
	peraturan := r.Group("/peraturan")
	{
		peraturan.POST("", h.Create)
		peraturan.GET("", h.GetList)
		peraturan.GET("/search", h.Search)
		peraturan.GET("/:id", h.GetByID)
		peraturan.PUT("/:id", h.Update)
		peraturan.DELETE("/:id", h.Delete)
	}
}
