import { Chart } from "@/components/ui/chart"
// Profile Module
const Profile = {
  // Configuration
  config: {
    chartColors: {
      primary: "#3b82f6",
      success: "#10b981",
      warning: "#f59e0b",
      danger: "#ef4444",
      info: "#06b6d4",
    },
    apiEndpoints: {
      updateProfile: "/api/profile/update",
      uploadAvatar: "/api/profile/avatar",
      markNotificationRead: "/api/notifications/mark-read",
      markAllNotificationsRead: "/api/notifications/mark-all-read",
    },
  },

  // State
  state: {
    activeTab: "overview",
    notifications: [],
    isUpdating: false,
  },

  // Initialize Profile
  init() {
    this.setupTabNavigation()
    this.setupAvatarUpload()
    this.setupProfileEdit()
    this.setupNotifications()
    this.setupCharts()
    this.loadInitialData()
  },

  // Setup Tab Navigation
  setupTabNavigation() {
    const navItems = document.querySelectorAll(".nav-item[data-tab]")
    const tabContents = document.querySelectorAll(".tab-content")

    navItems.forEach((item) => {
      item.addEventListener("click", (e) => {
        e.preventDefault()
        const tabId = item.getAttribute("data-tab")
        this.switchTab(tabId)
      })
    })
  },

  // Switch Tab
  switchTab(tabId) {
    // Update navigation
    document.querySelectorAll(".nav-item").forEach((item) => {
      item.classList.remove("active")
    })
    document.querySelector(`[data-tab="${tabId}"]`).classList.add("active")

    // Update content
    document.querySelectorAll(".tab-content").forEach((content) => {
      content.classList.remove("active")
    })
    document.getElementById(tabId).classList.add("active")

    this.state.activeTab = tabId

    // Load tab-specific data
    this.loadTabData(tabId)
  },

  // Load Tab Data
  loadTabData(tabId) {
    switch (tabId) {
      case "overview":
        this.loadOverviewData()
        break
      case "activity":
        this.loadActivityData()
        break
      case "notifications":
        this.loadNotifications()
        break
    }
  },

  // Setup Avatar Upload
  setupAvatarUpload() {
    const avatarUpload = document.getElementById("avatarUpload")
    const profileAvatar = document.querySelector(".profile-avatar")

    if (profileAvatar) {
      profileAvatar.addEventListener("click", () => {
        avatarUpload.click()
      })
    }

    if (avatarUpload) {
      avatarUpload.addEventListener("change", (e) => {
        const file = e.target.files[0]
        if (file) {
          this.uploadAvatar(file)
        }
      })
    }
  },

  // Upload Avatar
  async uploadAvatar(file) {
    // Validate file
    if (!file.type.startsWith("image/")) {
      this.showAlert("Por favor selecciona un archivo de imagen válido.", "danger")
      return
    }

    if (file.size > 5 * 1024 * 1024) {
      // 5MB
      this.showAlert("El archivo es demasiado grande. Máximo 5MB.", "danger")
      return
    }

    try {
      const formData = new FormData()
      formData.append("avatar", file)

      const response = await fetch(this.config.apiEndpoints.uploadAvatar, {
        method: "POST",
        body: formData,
      })

      const data = await response.json()

      if (response.ok) {
        // Update avatar image
        const avatarImg = document.querySelector("#profileAvatar")
        if (avatarImg) {
          avatarImg.src = data.avatarUrl
        }
        this.showAlert("Avatar actualizado exitosamente.", "success")
      } else {
        this.showAlert(data.message || "Error al subir el avatar.", "danger")
      }
    } catch (error) {
      console.error("Avatar upload error:", error)
      this.showAlert("Error de conexión. Por favor intenta nuevamente.", "danger")
    }
  },

  // Setup Profile Edit
  setupProfileEdit() {
    const editProfileForm = document.getElementById("editProfileForm")
    const saveProfileBtn = document.getElementById("saveProfileBtn")

    if (saveProfileBtn) {
      saveProfileBtn.addEventListener("click", () => {
        this.saveProfile()
      })
    }
  },

  // Save Profile
  async saveProfile() {
    if (this.state.isUpdating) return

    const form = document.getElementById("editProfileForm")
    const saveBtn = document.getElementById("saveProfileBtn")

    try {
      this.state.isUpdating = true
      this.setButtonLoading(saveBtn, true)

      const formData = new FormData(form)
      const response = await fetch(this.config.apiEndpoints.updateProfile, {
        method: "POST",
        body: formData,
      })

      const data = await response.json()

      if (response.ok) {
        this.showAlert("Perfil actualizado exitosamente.", "success")

        // Update profile display
        this.updateProfileDisplay(data.profile)

        // Close modal
        const modalElement = document.getElementById("editProfileModal")
        const modal = bootstrap.Modal.getInstance(modalElement)
        modal.hide()
      } else {
        this.showAlert(data.message || "Error al actualizar el perfil.", "danger")
      }
    } catch (error) {
      console.error("Profile update error:", error)
      this.showAlert("Error de conexión. Por favor intenta nuevamente.", "danger")
    } finally {
      this.state.isUpdating = false
      this.setButtonLoading(saveBtn, false)
    }
  },

  // Update Profile Display
  updateProfileDisplay(profileData) {
    // Update name
    const profileName = document.querySelector(".profile-name")
    if (profileName && profileData.firstName && profileData.lastName) {
      profileName.textContent = `${profileData.firstName} ${profileData.lastName}`
    }

    // Update other fields as needed
    const personalInfoInputs = document.querySelectorAll("#personal input")
    personalInfoInputs.forEach((input) => {
      if (profileData[input.name]) {
        input.value = profileData[input.name]
      }
    })
  },

  // Setup Notifications
  setupNotifications() {
    const markAllReadBtn = document.getElementById("markAllRead")

    if (markAllReadBtn) {
      markAllReadBtn.addEventListener("click", () => {
        this.markAllNotificationsRead()
      })
    }

    // Setup individual notification actions
    document.addEventListener("click", (e) => {
      if (e.target.matches(".notification-item .btn")) {
        const notificationItem = e.target.closest(".notification-item")
        if (notificationItem && notificationItem.classList.contains("unread")) {
          this.markNotificationRead(notificationItem)
        }
      }
    })
  },

  // Mark Notification as Read
  async markNotificationRead(notificationElement) {
    try {
      const notificationId = notificationElement.getAttribute("data-id")

      const response = await fetch(this.config.apiEndpoints.markNotificationRead, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ notificationId }),
      })

      if (response.ok) {
        notificationElement.classList.remove("unread")
        this.updateNotificationCount()
      }
    } catch (error) {
      console.error("Error marking notification as read:", error)
    }
  },

  // Mark All Notifications as Read
  async markAllNotificationsRead() {
    try {
      const response = await fetch(this.config.apiEndpoints.markAllNotificationsRead, {
        method: "POST",
      })

      if (response.ok) {
        document.querySelectorAll(".notification-item.unread").forEach((item) => {
          item.classList.remove("unread")
        })
        this.updateNotificationCount()
        this.showAlert("Todas las notificaciones marcadas como leídas.", "success")
      }
    } catch (error) {
      console.error("Error marking all notifications as read:", error)
    }
  },

  // Update Notification Count
  updateNotificationCount() {
    const unreadCount = document.querySelectorAll(".notification-item.unread").length
    const notificationCountElement = document.querySelector(".notification-count")

    if (notificationCountElement) {
      if (unreadCount > 0) {
        notificationCountElement.textContent = unreadCount
        notificationCountElement.style.display = "inline-block"
      } else {
        notificationCountElement.style.display = "none"
      }
    }
  },

  // Setup Charts
  setupCharts() {
    this.setupProgressChart()
  },

  // Setup Progress Chart
  setupProgressChart() {
    const canvas = document.getElementById("progressChart")
    if (!canvas) return

    const ctx = canvas.getContext("2d")

    new Chart(ctx, {
      type: "line",
      data: {
        labels: ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio"],
        datasets: [
          {
            label: "Calificaciones",
            data: [3.8, 4.1, 3.9, 4.3, 4.2, 4.5],
            borderColor: this.config.chartColors.primary,
            backgroundColor: this.config.chartColors.primary + "20",
            tension: 0.4,
            fill: true,
          },
          {
            label: "Participación",
            data: [85, 88, 82, 91, 89, 92],
            borderColor: this.config.chartColors.success,
            backgroundColor: this.config.chartColors.success + "20",
            tension: 0.4,
            fill: true,
            yAxisID: "y1",
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "top",
          },
          title: {
            display: false,
          },
        },
        scales: {
          y: {
            type: "linear",
            display: true,
            position: "left",
            min: 0,
            max: 5,
            title: {
              display: true,
              text: "Calificación",
            },
          },
          y1: {
            type: "linear",
            display: true,
            position: "right",
            min: 0,
            max: 100,
            title: {
              display: true,
              text: "Participación (%)",
            },
            grid: {
              drawOnChartArea: false,
            },
          },
        },
      },
    })
  },

  // Load Initial Data
  loadInitialData() {
    this.loadOverviewData()
    this.updateNotificationCount()
  },

  // Load Overview Data
  loadOverviewData() {
    // This would typically fetch data from an API
    // For now, we'll use the static data already in the HTML
    console.log("Loading overview data...")
  },

  // Load Activity Data
  loadActivityData() {
    // This would typically fetch recent activity from an API
    console.log("Loading activity data...")
  },

  // Load Notifications
  loadNotifications() {
    // This would typically fetch notifications from an API
    console.log("Loading notifications...")
  },

  // Set Button Loading State
  setButtonLoading(button, isLoading) {
    if (isLoading) {
      button.disabled = true
      const originalText = button.innerHTML
      button.setAttribute("data-original-text", originalText)
      button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Guardando...'
    } else {
      button.disabled = false
      const originalText = button.getAttribute("data-original-text")
      if (originalText) {
        button.innerHTML = originalText
      }
    }
  },

  // Show Alert
  showAlert(message, type = "info") {
    // Create toast notification
    const toast = document.createElement("div")
    toast.className = `toast align-items-center text-white bg-${type} border-0`
    toast.setAttribute("role", "alert")
    toast.setAttribute("aria-live", "assertive")
    toast.setAttribute("aria-atomic", "true")

    toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${type === "success" ? "check-circle" : type === "danger" ? "exclamation-triangle" : "info-circle"} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `

    // Add to toast container or create one
    let toastContainer = document.querySelector(".toast-container")
    if (!toastContainer) {
      toastContainer = document.createElement("div")
      toastContainer.className = "toast-container position-fixed top-0 end-0 p-3"
      toastContainer.style.zIndex = "1055"
      document.body.appendChild(toastContainer)
    }

    toastContainer.appendChild(toast)

    // Initialize and show toast
    const bsToast = new bootstrap.Toast(toast)
    bsToast.show()

    // Remove toast element after it's hidden
    toast.addEventListener("hidden.bs.toast", () => {
      toast.remove()
    })
  },
}

// Export for use in other modules
if (typeof module !== "undefined" && module.exports) {
  module.exports = Profile
}
