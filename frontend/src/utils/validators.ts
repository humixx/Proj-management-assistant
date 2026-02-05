export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

export const validators = {
  required: (value: string, fieldName: string): ValidationResult => {
    if (!value || !value.trim()) {
      return { isValid: false, error: `${fieldName} is required` };
    }
    return { isValid: true };
  },

  minLength: (value: string, min: number, fieldName: string): ValidationResult => {
    if (value.length < min) {
      return { isValid: false, error: `${fieldName} must be at least ${min} characters` };
    }
    return { isValid: true };
  },

  maxLength: (value: string, max: number, fieldName: string): ValidationResult => {
    if (value.length > max) {
      return { isValid: false, error: `${fieldName} must be less than ${max} characters` };
    }
    return { isValid: true };
  },

  email: (value: string, fieldName: string): ValidationResult => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(value)) {
      return { isValid: false, error: `${fieldName} must be a valid email address` };
    }
    return { isValid: true };
  },

  url: (value: string, fieldName: string): ValidationResult => {
    try {
      new URL(value);
      return { isValid: true };
    } catch {
      return { isValid: false, error: `${fieldName} must be a valid URL` };
    }
  },

  // Combine multiple validations
  validate: (value: string, rules: ValidationResult[]): ValidationResult => {
    for (const rule of rules) {
      if (!rule.isValid) return rule;
    }
    return { isValid: true };
  },
};

// Project validation
export const validateProjectName = (name: string): ValidationResult => {
  return validators.validate(name, [
    validators.required(name, 'Project name'),
    validators.minLength(name, 2, 'Project name'),
    validators.maxLength(name, 100, 'Project name'),
  ]);
};

export const validateProjectDescription = (description: string): ValidationResult => {
  if (description && description.length > 500) {
    return { isValid: false, error: 'Project description must be less than 500 characters' };
  }
  return { isValid: true };
};

// Task validation
export const validateTaskTitle = (title: string): ValidationResult => {
  return validators.validate(title, [
    validators.required(title, 'Task title'),
    validators.minLength(title, 2, 'Task title'),
    validators.maxLength(title, 200, 'Task title'),
  ]);
};

export const validateTaskDescription = (description: string): ValidationResult => {
  if (description && description.length > 1000) {
    return { isValid: false, error: 'Task description must be less than 1000 characters' };
  }
  return { isValid: true };
};

// Team member validation
export const validateEmail = (email: string): ValidationResult => {
  return validators.validate(email, [
    validators.required(email, 'Email'),
    validators.email(email, 'Email'),
  ]);
};// Document validation
export const validateFileName = (fileName: string): ValidationResult => {
  return validators.validate(fileName, [
    validators.required(fileName, 'File name'),
    validators.minLength(fileName, 1, 'File name'),
    validators.maxLength(fileName, 255, 'File name'),
  ]);
};
