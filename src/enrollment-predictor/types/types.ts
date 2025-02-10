export interface ComparisonResponse {
  text: string;
}

export interface EnrollmentData {
  id: number;
  year: number;
  students: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface MailingInfo {
  id: number;
  mailing_city: string;
  mailing_state_province: string;
  mailing_zip_postal_code: string;
  mailing_country: string;
  start_term_year: string;
}

export interface MailingInfoListResponse {
  total: number;
  records: MailingInfo[];
}

export interface DeleteResponse {
  message: string;
}

export interface UploadResponse {
  message: string;
}

export interface ErrorResponse {
  error: string;
}

export interface EnrollmentDataResponse {
  historical: EnrollmentData[];
  predicted: EnrollmentData[];
  ai_context: string;
}
