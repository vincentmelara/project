import { DropdownModule } from 'primeng/dropdown';
import { Component, AfterViewInit, OnDestroy } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { HeatmapComponent } from "./heatmap/heatmap.component";
import { VoronoiMapComponent } from "./voronoi-map/voronoi-map.component"; // ✅ Ensure Basemap is imported
import { CommonModule } from '@angular/common';
@Component({
  selector: 'app-heatmap-page',
  standalone: true,
  imports: [
    DropdownModule,
    ButtonModule,
    HeatmapComponent,
    VoronoiMapComponent,
    CommonModule
],
  templateUrl: './heatmap-page.component.html',
  styleUrl: './heatmap-page.component.css'

})
export class HeatmapPageComponent {
  activeMap: 'heatmap' | 'voronoi' = 'heatmap'; // Default to Heatmap

  switchMap(): void {
    this.activeMap = this.activeMap === 'heatmap' ? 'voronoi' : 'heatmap';
  }
  resetMap(): void {
    // Optionally, reset other map parameters here if needed
    this.activeMap = 'heatmap'; // Reset to default view
  }
}
