import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HeatmapPageComponent } from './heatmap-page.component';

describe('HeatmapPageComponent', () => {
  let component: HeatmapPageComponent;
  let fixture: ComponentFixture<HeatmapPageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HeatmapPageComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HeatmapPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
