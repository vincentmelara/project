import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class EnrollmentService {
  private apiUrl = 'http://localhost:8001/api/enrollment-data';
  private compareUrl = 'http://localhost:8001/api/generate-comparison';

  constructor(private http: HttpClient) {}

  getEnrollmentData(): Observable<any> {
    return this.http.get<any>(this.apiUrl);
  }

  generateComparison(prompt: string): Observable<any> {
    return this.http.post<any>(this.compareUrl, { prompt });
  }
}
