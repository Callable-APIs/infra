# SSH Key Management Variables

variable "oracle_arm_1_ip" {
  description = "Public IP of Oracle Cloud ARM instance 1"
  type        = string
  default     = ""
}

variable "oracle_arm_2_ip" {
  description = "Public IP of Oracle Cloud ARM instance 2"
  type        = string
  default     = ""
}

variable "google_e2_micro_ip" {
  description = "Public IP of Google Cloud e2-micro instance"
  type        = string
  default     = ""
}

variable "ibm_vsi_ip" {
  description = "Public IP of IBM Cloud VSI instance"
  type        = string
  default     = ""
}

variable "aws_eb_ip" {
  description = "Public IP of AWS Elastic Beanstalk instance"
  type        = string
  default     = ""
}

