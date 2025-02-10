import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { debounce } from 'lodash';
import { EnrollmentService } from '../services/enrollment.service';

import { CardModule } from 'primeng/card';
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { NgxChartsModule } from '@swimlane/ngx-charts';

interface EnrollmentData {
  year: number;
  students: number;
}

@Component({
  selector: 'app-enrollment-predictor',
  standalone: true,
  imports: [
    CardModule,
    ProgressSpinnerModule,
    NgxChartsModule
  ],
  templateUrl: './enrollment-predictor.component.html',
  styleUrls: ['./enrollment-predictor.component.css'],
  providers: [EnrollmentService]
})
export class EnrollmentPredictorComponent implements OnInit {
  historicalData: EnrollmentData[] = [];
  predictedData: EnrollmentData[] = [];
  aiContext: string = '';
  combinedData: EnrollmentData[] = [];
  loading = true;
  error: string | null = null;

  comparisonResult: string = '';
  showModal = false;
  comparisonLoading = false;

  constructor(private http: HttpClient, private enrollmentService: EnrollmentService) {}

  ngOnInit() {
    this.fetchEnrollmentData();
  }

  fetchEnrollmentData() {
    this.enrollmentService.getEnrollmentData().subscribe({
      next: (data) => {
        this.historicalData = data.historical || [];
        this.predictedData = data.predicted || [];
        this.aiContext = data.ai_context;
        this.combineData();
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to fetch enrollment data';
        this.loading = false;
      }
    });
  }

  combineData() {
    this.combinedData = [...this.historicalData, ...this.predictedData].sort((a, b) => a.year - b.year);
  }

  generateComparison(selectedDataPoint: EnrollmentData) {
    const previousYearData = this.combinedData.find((d) => d.year === selectedDataPoint.year - 1);
    if (!previousYearData) {
      alert('Previous year data not available.');
      return;
    }

    const prompt = `${this.aiContext}
Compare the enrollment of ${selectedDataPoint.students} students in ${selectedDataPoint.year}
with ${previousYearData.students} students in ${previousYearData.year}.`;

    this.comparisonLoading = true;
    this.showModal = true;

    this.enrollmentService.generateComparison(prompt).subscribe({
      next: (response) => {
        this.comparisonResult = response.text;
        this.comparisonLoading = false;
      },
      error: () => {
        this.comparisonResult = 'An error occurred while generating the comparison.';
        this.comparisonLoading = false;
      }
    });
  }

  debouncedGenerateComparison = debounce((dataPoint: EnrollmentData) => {
    this.generateComparison(dataPoint);
  }, 500);
}
