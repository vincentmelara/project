import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VoronoiMapComponent } from './voronoi-map.component';

describe('VoronoiMapComponent', () => {
  let component: VoronoiMapComponent;
  let fixture: ComponentFixture<VoronoiMapComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VoronoiMapComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(VoronoiMapComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
