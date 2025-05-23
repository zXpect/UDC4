// Auth Module
const Auth = {
  // Configuration
  config: {
    passwordMinLength: 8,
    usernameMinLength: 4,
    usernameMaxLength: 20,
    debounceDelay: 500,
    apiEndpoints: {
      checkUsername: "/api/check-username",
      checkEmail: "/api/check-email",
      login: "/auth/login",
      register: "/auth/register",
      forgotPassword: "/auth/forgot-password",
    },
  },

  // State
  state: {
    currentStep: 1,
    totalSteps: 3,
    formData: {},
    validationState: {},
    isSubmitting: false,
  },

  // Initialize Login Form
  initLogin() {
    this.setupPasswordToggle()
    this.setupLoginValidation()
    this.setupLoginForm()
    this.setupForgotPassword()
  },

  // Initialize Register Form
  initRegister() {
    this.setupPasswordToggle()
    this.setupRegisterValidation()
    this.setupStepNavigation()
    this.setupRegisterForm()
    this.setupRoleSelector()
    this.setupPasswordStrength()
  },

  // Password Toggle Functionality
  setupPasswordToggle() {
    document.querySelectorAll(".password-toggle").forEach((toggle) => {
      toggle.addEventListener("click", (e) => {
        e.preventDefault()
        const targetId = toggle.getAttribute("data-target")
        const passwordInput = document.getElementById(targetId)
        const icon = toggle.querySelector("i")

        if (passwordInput.type === "password") {
          passwordInput.type = "text"
          icon.classList.remove("fa-eye")
          icon.classList.add("fa-eye-slash")
        } else {
          passwordInput.type = "password"
          icon.classList.remove("fa-eye-slash")
          icon.classList.add("fa-eye")
        }
      })
    })
  },

  // Login Validation
  setupLoginValidation() {
    const form = document.getElementById("loginForm")
    if (!form) return

    const inputs = form.querySelectorAll("input[data-validate]")
    inputs.forEach((input) => {
      input.addEventListener("blur", () => this.validateField(input))
      input.addEventListener(
        "input",
        this.debounce(() => this.validateField(input), 300),
      )
    })
  },

  // Register Validation
  setupRegisterValidation() {
    const form = document.getElementById("registerForm")
    if (!form) return

    const inputs = form.querySelectorAll("input[data-validate]")
    inputs.forEach((input) => {
      input.addEventListener("blur", () => this.validateField(input))
      input.addEventListener(
        "input",
        this.debounce(() => this.validateField(input), 300),
      )
    })

    // Special handling for username and email availability
    const usernameInput = document.getElementById("username")
    const emailInput = document.getElementById("email")

    if (usernameInput) {
      usernameInput.addEventListener(
        "input",
        this.debounce(() => this.checkAvailability(usernameInput, "username"), this.config.debounceDelay),
      )
    }

    if (emailInput) {
      emailInput.addEventListener(
        "input",
        this.debounce(() => this.checkAvailability(emailInput, "email"), this.config.debounceDelay),
      )
    }
  },

  // Field Validation
  validateField(input) {
    const validationType = input.getAttribute("data-validate")
    const value = input.value.trim()
    let isValid = true
    let message = ""

    switch (validationType) {
      case "username":
        if (value.length < this.config.usernameMinLength) {
          isValid = false
          message = `El nombre de usuario debe tener al menos ${this.config.usernameMinLength} caracteres`
        } else if (value.length > this.config.usernameMaxLength) {
          isValid = false
          message = `El nombre de usuario no puede tener más de ${this.config.usernameMaxLength} caracteres`
        } else if (!/^[a-zA-Z0-9_]+$/.test(value)) {
          isValid = false
          message = "Solo se permiten letras, números y guiones bajos"
        } else {
          message = "Nombre de usuario válido"
        }
        break

      case "email":
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        if (!emailRegex.test(value)) {
          isValid = false
          message = "Ingresa un correo electrónico válido"
        } else {
          message = "Correo electrónico válido"
        }
        break

      case "password":
        const passwordValidation = this.validatePassword(value)
        isValid = passwordValidation.isValid
        message = passwordValidation.message
        break

      case "confirmPassword":
        const passwordInput = document.getElementById("password")
        if (passwordInput && value !== passwordInput.value) {
          isValid = false
          message = "Las contraseñas no coinciden"
        } else if (value === passwordInput.value && value.length > 0) {
          message = "Las contraseñas coinciden"
        }
        break

      case "name":
        if (value.length < 2) {
          isValid = false
          message = "Debe tener al menos 2 caracteres"
        } else if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(value)) {
          isValid = false
          message = "Solo se permiten letras y espacios"
        } else {
          message = "Nombre válido"
        }
        break

      default:
        if (input.hasAttribute("required") && value === "") {
          isValid = false
          message = "Este campo es obligatorio"
        }
        break
    }

    this.updateFieldValidation(input, isValid, message)
    this.state.validationState[input.name] = isValid

    return isValid
  },

  // Password Validation
  validatePassword(password) {
    const requirements = {
      length: password.length >= this.config.passwordMinLength,
      uppercase: /[A-Z]/.test(password),
      lowercase: /[a-z]/.test(password),
      number: /\d/.test(password),
    }

    const metRequirements = Object.values(requirements).filter(Boolean).length
    const isValid = metRequirements === 4

    let strength = "weak"
    let message = "Muy débil"

    if (metRequirements >= 4) {
      strength = "strong"
      message = "Muy fuerte"
    } else if (metRequirements >= 3) {
      strength = "good"
      message = "Buena"
    } else if (metRequirements >= 2) {
      strength = "fair"
      message = "Regular"
    }

    // Update password requirements UI
    this.updatePasswordRequirements(requirements)
    this.updatePasswordStrength(strength, message)

    return {
      isValid,
      strength,
      message: isValid ? "Contraseña segura" : "La contraseña no cumple todos los requisitos",
      requirements,
    }
  },

  // Update Field Validation UI
  updateFieldValidation(input, isValid, message) {
    const wrapper = input.closest(".input-wrapper")
    const feedback = wrapper.querySelector(".input-feedback")

    // Update input classes
    input.classList.remove("is-valid", "is-invalid")
    input.classList.add(isValid ? "is-valid" : "is-invalid")

    // Update feedback message
    if (feedback) {
      feedback.textContent = message
      feedback.classList.remove("valid", "invalid")
      feedback.classList.add(isValid ? "valid" : "invalid")
    }
  },

  // Check Username/Email Availability
  async checkAvailability(input, type) {
    const value = input.value.trim()
    if (value.length < 3) return

    const wrapper = input.closest(".input-wrapper")
    const availabilityCheck = wrapper.querySelector(".availability-check")

    if (!availabilityCheck) return

    // Show checking state
    availabilityCheck.className = "availability-check checking"
    availabilityCheck.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>Verificando disponibilidad...</span>'

    try {
      const endpoint =
        type === "username" ? this.config.apiEndpoints.checkUsername : this.config.apiEndpoints.checkEmail
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ [type]: value }),
      })

      const data = await response.json()

      if (data.available) {
        availabilityCheck.className = "availability-check available"
        availabilityCheck.innerHTML = '<i class="fas fa-check"></i> <span>Disponible</span>'
        this.updateFieldValidation(input, true, `${type === "username" ? "Nombre de usuario" : "Correo"} disponible`)
      } else {
        availabilityCheck.className = "availability-check unavailable"
        availabilityCheck.innerHTML = '<i class="fas fa-times"></i> <span>No disponible</span>'
        this.updateFieldValidation(
          input,
          false,
          `Este ${type === "username" ? "nombre de usuario" : "correo"} ya está en uso`,
        )
      }
    } catch (error) {
      console.error("Error checking availability:", error)
      availabilityCheck.style.display = "none"
    }
  },

  // Update Password Requirements UI
  updatePasswordRequirements(requirements) {
    const requirementElements = document.querySelectorAll(".requirement")

    requirementElements.forEach((element) => {
      const requirement = element.getAttribute("data-requirement")
      const icon = element.querySelector("i")

      if (requirements[requirement]) {
        element.classList.add("met")
        icon.classList.remove("fa-times")
        icon.classList.add("fa-check")
      } else {
        element.classList.remove("met")
        icon.classList.remove("fa-check")
        icon.classList.add("fa-times")
      }
    })
  },

  // Update Password Strength UI
  updatePasswordStrength(strength, message) {
    const strengthFill = document.querySelector(".strength-fill")
    const strengthText = document.querySelector(".strength-text")

    if (strengthFill) {
      strengthFill.className = `strength-fill ${strength}`
    }

    if (strengthText) {
      strengthText.textContent = message
      strengthText.className = `strength-text ${strength}`
    }
  },

  // Setup Step Navigation
  setupStepNavigation() {
    const nextBtn = document.getElementById("nextBtn")
    const prevBtn = document.getElementById("prevBtn")
    const submitBtn = document.getElementById("submitBtn")

    if (nextBtn) {
      nextBtn.addEventListener("click", () => this.nextStep())
    }

    if (prevBtn) {
      prevBtn.addEventListener("click", () => this.prevStep())
    }
  },

  // Next Step
  nextStep() {
    if (!this.validateCurrentStep()) {
      this.showAlert("Por favor completa todos los campos correctamente antes de continuar.", "danger")
      return
    }

    if (this.state.currentStep < this.state.totalSteps) {
      this.state.currentStep++
      this.updateStepDisplay()
      this.updateFormData()
    }
  },

  // Previous Step
  prevStep() {
    if (this.state.currentStep > 1) {
      this.state.currentStep--
      this.updateStepDisplay()
    }
  },

  // Validate Current Step
  validateCurrentStep() {
    const currentStepElement = document.querySelector(`.form-step[data-step="${this.state.currentStep}"]`)
    const inputs = currentStepElement.querySelectorAll("input[required], select[required]")
    let isValid = true

    inputs.forEach((input) => {
      if (input.type === "radio") {
        const radioGroup = currentStepElement.querySelectorAll(`input[name="${input.name}"]`)
        const isChecked = Array.from(radioGroup).some((radio) => radio.checked)
        if (!isChecked) {
          isValid = false
        }
      } else if (!this.validateField(input)) {
        isValid = false
      }
    })

    return isValid
  },

  // Update Step Display
  updateStepDisplay() {
    // Update step indicators
    document.querySelectorAll(".step").forEach((step, index) => {
      const stepNumber = index + 1
      step.classList.remove("active", "completed")

      if (stepNumber < this.state.currentStep) {
        step.classList.add("completed")
      } else if (stepNumber === this.state.currentStep) {
        step.classList.add("active")
      }
    })

    // Update form steps
    document.querySelectorAll(".form-step").forEach((step, index) => {
      const stepNumber = index + 1
      step.classList.remove("active")

      if (stepNumber === this.state.currentStep) {
        step.classList.add("active")
      }
    })

    // Update navigation buttons
    const nextBtn = document.getElementById("nextBtn")
    const prevBtn = document.getElementById("prevBtn")
    const submitBtn = document.getElementById("submitBtn")

    if (prevBtn) {
      prevBtn.style.display = this.state.currentStep > 1 ? "block" : "none"
    }

    if (nextBtn && submitBtn) {
      if (this.state.currentStep === this.state.totalSteps) {
        nextBtn.style.display = "none"
        submitBtn.style.display = "block"
        this.updateAccountSummary()
      } else {
        nextBtn.style.display = "block"
        submitBtn.style.display = "none"
      }
    }
  },

  // Update Form Data
  updateFormData() {
    const form = document.getElementById("registerForm")
    const formData = new FormData(form)

    for (const [key, value] of formData.entries()) {
      this.state.formData[key] = value
    }
  },

  // Update Account Summary
  updateAccountSummary() {
    const summaryName = document.getElementById("summaryName")
    const summaryEmail = document.getElementById("summaryEmail")
    const summaryUsername = document.getElementById("summaryUsername")
    const summaryRole = document.getElementById("summaryRole")

    if (summaryName) {
      summaryName.textContent = `${this.state.formData.firstName || ""} ${this.state.formData.lastName || ""}`.trim()
    }
    if (summaryEmail) {
      summaryEmail.textContent = this.state.formData.email || ""
    }
    if (summaryUsername) {
      summaryUsername.textContent = this.state.formData.username || ""
    }
    if (summaryRole) {
      const roleLabels = {
        student: "Estudiante",
        teacher: "Profesor",
        admin: "Administrador",
      }
      summaryRole.textContent = roleLabels[this.state.formData.role] || ""
    }
  },

  // Setup Role Selector
  setupRoleSelector() {
    const roleOptions = document.querySelectorAll(".role-option")

    roleOptions.forEach((option) => {
      option.addEventListener("click", () => {
        const radio = option.querySelector('input[type="radio"]')
        radio.checked = true

        // Update visual state
        roleOptions.forEach((opt) => opt.classList.remove("selected"))
        option.classList.add("selected")
      })
    })
  },

  // Setup Password Strength
  setupPasswordStrength() {
    const passwordInput = document.getElementById("password")
    if (!passwordInput) return

    passwordInput.addEventListener("input", () => {
      const password = passwordInput.value
      this.validatePassword(password)
    })
  },

  // Setup Login Form
  setupLoginForm() {
    const form = document.getElementById("loginForm")
    if (!form) return

    form.addEventListener("submit", async (e) => {
      e.preventDefault()

      if (this.state.isSubmitting) return

      const isValid = this.validateLoginForm()
      if (!isValid) return

      await this.submitLogin(form)
    })
  },

  // Setup Register Form
  setupRegisterForm() {
    const form = document.getElementById("registerForm")
    if (!form) return

    form.addEventListener("submit", async (e) => {
      e.preventDefault()

      if (this.state.isSubmitting) return

      const isValid = this.validateRegisterForm()
      if (!isValid) return

      await this.submitRegister(form)
    })
  },

  // Validate Login Form
  validateLoginForm() {
    const form = document.getElementById("loginForm")
    const inputs = form.querySelectorAll("input[required]")
    let isValid = true

    inputs.forEach((input) => {
      if (!this.validateField(input)) {
        isValid = false
      }
    })

    return isValid
  },

  // Validate Register Form
  validateRegisterForm() {
    const form = document.getElementById("registerForm")
    const inputs = form.querySelectorAll("input[required], select[required]")
    let isValid = true

    inputs.forEach((input) => {
      if (input.type === "radio") {
        const radioGroup = form.querySelectorAll(`input[name="${input.name}"]`)
        const isChecked = Array.from(radioGroup).some((radio) => radio.checked)
        if (!isChecked) {
          isValid = false
        }
      } else if (!this.validateField(input)) {
        isValid = false
      }
    })

    // Check terms acceptance
    const termsCheckbox = document.getElementById("terms")
    if (termsCheckbox && !termsCheckbox.checked) {
      isValid = false
      this.showAlert("Debes aceptar los términos y condiciones para continuar.", "danger")
    }

    return isValid
  },

  // Submit Login
  async submitLogin(form) {
    const submitBtn = document.getElementById("loginBtn")

    try {
      this.state.isSubmitting = true
      this.setButtonLoading(submitBtn, true)

      const formData = new FormData(form)
      const response = await fetch(this.config.apiEndpoints.login, {
        method: "POST",
        body: formData,
      })

      const data = await response.json()

      if (response.ok) {
        this.showAlert("¡Inicio de sesión exitoso! Redirigiendo...", "success")
        setTimeout(() => {
          window.location.href = data.redirect || "/dashboard"
        }, 1500)
      } else {
        this.showAlert(data.message || "Error al iniciar sesión. Verifica tus credenciales.", "danger")
      }
    } catch (error) {
      console.error("Login error:", error)
      this.showAlert("Error de conexión. Por favor intenta nuevamente.", "danger")
    } finally {
      this.state.isSubmitting = false
      this.setButtonLoading(submitBtn, false)
    }
  },

  // Submit Register
  async submitRegister(form) {
    const submitBtn = document.getElementById("submitBtn")

    try {
      this.state.isSubmitting = true
      this.setButtonLoading(submitBtn, true)

      const formData = new FormData(form)
      const response = await fetch(this.config.apiEndpoints.register, {
        method: "POST",
        body: formData,
      })

      const data = await response.json()

      if (response.ok) {
        this.showAlert("¡Cuenta creada exitosamente! Redirigiendo...", "success")
        setTimeout(() => {
          window.location.href = data.redirect || "/auth/login"
        }, 1500)
      } else {
        this.showAlert(data.message || "Error al crear la cuenta. Por favor intenta nuevamente.", "danger")
      }
    } catch (error) {
      console.error("Register error:", error)
      this.showAlert("Error de conexión. Por favor intenta nuevamente.", "danger")
    } finally {
      this.state.isSubmitting = false
      this.setButtonLoading(submitBtn, false)
    }
  },

  // Setup Forgot Password
  setupForgotPassword() {
    const form = document.getElementById("forgotPasswordForm")
    if (!form) return

    form.addEventListener("submit", async (e) => {
      e.preventDefault()
      await this.submitForgotPassword(form)
    })
  },

  // Submit Forgot Password
  async submitForgotPassword(form) {
    try {
      const formData = new FormData(form)
      const response = await fetch(this.config.apiEndpoints.forgotPassword, {
        method: "POST",
        body: formData,
      })

      const data = await response.json()

      if (response.ok) {
        this.showAlert("Se ha enviado un enlace de recuperación a tu correo electrónico.", "success")
        const modalElement = document.getElementById("forgotPasswordModal")
        const modal = bootstrap.Modal.getInstance(modalElement)
        if (modal) {
          modal.hide()
        }
      } else {
        this.showAlert(data.message || "Error al enviar el enlace de recuperación.", "danger")
      }
    } catch (error) {
      console.error("Forgot password error:", error)
      this.showAlert("Error de conexión. Por favor intenta nuevamente.", "danger")
    }
  },

  // Set Button Loading State
  setButtonLoading(button, isLoading) {
    if (isLoading) {
      button.classList.add("loading")
      button.disabled = true
    } else {
      button.classList.remove("loading")
      button.disabled = false
    }
  },

  // Show Alert
  showAlert(message, type = "info") {
    const alertContainer = document.querySelector(".alert-container")
    if (!alertContainer) return

    const alertElement = document.createElement("div")
    alertElement.className = `alert alert-${type}`
    alertElement.innerHTML = `
            <i class="fas fa-${type === "success" ? "check-circle" : type === "danger" ? "exclamation-triangle" : "info-circle"}"></i>
            ${message}
        `

    alertContainer.innerHTML = ""
    alertContainer.appendChild(alertElement)

    // Auto-hide success messages
    if (type === "success") {
      setTimeout(() => {
        alertElement.remove()
      }, 5000)
    }
  },

  // Debounce Utility
  debounce(func, wait) {
    let timeout
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout)
        func(...args)
      }
      clearTimeout(timeout)
      timeout = setTimeout(later, wait)
    }
  },
}

// Export for use in other modules
if (typeof module !== "undefined" && module.exports) {
  module.exports = Auth
}
