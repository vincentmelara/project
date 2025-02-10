import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EnrollmentPredictorComponent } from './enrollment-predictor.component';

describe('EnrollmentPredictorComponent', () => {
  let component: EnrollmentPredictorComponent;
  let fixture: ComponentFixture<EnrollmentPredictorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EnrollmentPredictorComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(EnrollmentPredictorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
