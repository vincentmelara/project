import { DropdownModule } from 'primeng/dropdown';
import { Component, AfterViewInit, OnDestroy } from '@angular/core';
import WebMap from '@arcgis/core/WebMap';
import MapView from '@arcgis/core/views/MapView';
import FeatureLayer from '@arcgis/core/layers/FeatureLayer';
import HeatmapRenderer from '@arcgis/core/renderers/HeatmapRenderer';
import Search from '@arcgis/core/widgets/Search';
import Legend from '@arcgis/core/widgets/Legend';
import Expand from '@arcgis/core/widgets/Expand';
import Graphic from '@arcgis/core/Graphic';
import { ButtonModule } from 'primeng/button';
import { zipCodeData } from '../assets/data/ZipCodeData'; // Replace with the path to your zip code data
import Point from '@arcgis/core/geometry/Point'; // Import Point explicitly
import Basemap from '@arcgis/core/Basemap'; // ✅ Ensure Basemap is imported


@Component({
  selector: 'app-heatmap',
  standalone: true,
  imports: [
    DropdownModule,
    ButtonModule
  ],
  templateUrl: './heatmap.component.html',
  styleUrl: './heatmap.component.css'

})
export class HeatmapComponent implements AfterViewInit, OnDestroy {
  private mapView!: MapView;
  featureLayer!: FeatureLayer;

  colorScheme: 'Red' | 'Blue' | 'Purple' = 'Red'; // Default color scheme
  baseMap = 'streets';
  blurRadius = 10;
  maxPixelIntensity = 24;

  colorSchemeOptions = [
    { label: 'Red', value: 'Red' },
    { label: 'Blue', value: 'Blue' },
    { label: 'Purple', value: 'Purple' },
  ];

  basemapOptions = [
    { label: 'Streets', value: 'streets' },
    { label: 'Satellite', value: 'satellite' },
    { label: 'Hybrid', value: 'hybrid' },
    { label: 'Topographic', value: 'topo' },
    { label: 'Dark Gray', value: 'dark-gray' },
    { label: 'Gray', value: 'gray' },
    { label: 'National Geographic', value: 'national-geographic' },
  ];

  ngAfterViewInit(): void {
    const webmap = new WebMap({ basemap: this.baseMap });

    this.mapView = new MapView({
      container: 'heatmapView',
      map: webmap,
      zoom: 4,
      center: [-117.201757, 34.872701],
      popup: {
        dockEnabled: false,
        // autoOpenEnabled: true,
      },
    });

    this.featureLayer = new FeatureLayer({
      source: zipCodeData
      .filter(entry => entry.LNG !== null && entry.LAT !== null) // Filter invalid entries
      .map((entry, index) => ({
        geometry: new Point({
          // type: 'point',
          longitude: entry.LNG as number,
          latitude: entry.LAT as number,
        }),
        attributes: {
          ObjectID: index,
          Zip_Code: entry.Zip_Code,
          Count: entry.Count
        },
      })),
      objectIdField: 'ObjectID',
      fields: [
        { name: 'ObjectID', alias: 'ObjectID', type: 'oid' },
        { name: 'Zip_Code', alias: 'Zip Code', type: 'string' },
        { name: 'Count', alias: 'Student Count', type: 'integer' },
      ],
      popupTemplate: {
        title: 'Zip Code: {Zip_Code}',
        content: 'Student Count: {Count}',
      },
    });

    webmap.add(this.featureLayer);


    const searchWidget = new Search({
      view: this.mapView, // Attach to the MapView
      sources: [
        {
          layer: this.featureLayer, // Your FeatureLayer instance
          searchFields: ['Zip_Code'], // Fields used for matching search queries
          displayField: 'Zip_Code', // Field to display in search results
          exactMatch: false, // Allow partial matches
          outFields: ['Zip_Code', 'Count'], // Fields included in search results
          name: 'Zip Code Search', // Name for the search source
          placeholder: 'Enter Zip Code', // Placeholder text for the input box
        } as unknown as __esri.LayerSearchSource, // Explicitly cast to LayerSearchSource
      ],
    });

    // Add the Search widget to the MapView UI
    this.mapView.ui.add(searchWidget, 'top-right');


    const legend = new Legend({
      view: this.mapView,
      layerInfos: [{ layer: this.featureLayer }],
    });
    const legendExpand = new Expand({
      view: this.mapView,
      content: legend,
    });
    this.mapView.ui.add(legendExpand, 'top-left');

    this.updateHeatmapRenderer();
  }

  updateHeatmapRenderer(): void {
    // Define the color stops for each color scheme
    const colorStops: { [key in 'Red' | 'Blue' | 'Purple']: { ratio: number; color: string }[] } = {
      Red: [
        { ratio: 0, color: 'rgba(255, 255, 255, 0)' },
        { ratio: 0.5, color: 'rgba(255, 140, 0, 1)' },
        { ratio: 0.8, color: 'rgba(255, 0, 0, 1)' },
      ],
      Blue: [
        { ratio: 0, color: 'rgba(0, 255, 255, 0)' },
        { ratio: 0.5, color: 'rgba(0, 140, 255, 0.8)' },
        { ratio: 1, color: 'rgba(0, 0, 255, 1)' },
      ],
      Purple: [
        { ratio: 0, color: 'rgba(0, 0, 0, 0)' },
        { ratio: 0.5, color: 'rgba(218, 207, 255, 1)' },
        { ratio: 1, color: 'rgba(191, 0, 255, 1)' },
      ],
    };

    // Create the heatmap renderer
    const heatmapRenderer = new HeatmapRenderer({
      field: 'Count', // Field used for heatmap generation
      colorStops: colorStops[this.colorScheme], // Use the selected color scheme
      blurRadius: this.blurRadius, // Blur radius for smoothing the heatmap
      maxPixelIntensity: this.maxPixelIntensity, // Maximum intensity for rendering
      minPixelIntensity: 10, // Minimum intensity for rendering
    } as __esri.HeatmapRendererProperties); // Explicitly cast to HeatmapRendererProperties

    // Update the renderer of the FeatureLayer
    this.featureLayer.renderer = heatmapRenderer;
  }


  updateBasemap(): void {
    this.mapView.map.basemap = Basemap.fromId(this.baseMap); // Correct way to set basemap
  }

  resetDefaults(): void {
    this.colorScheme = 'Red';
    this.baseMap = 'streets';
    this.blurRadius = 15;
    this.maxPixelIntensity = 250;
    this.updateHeatmapRenderer();
  }

  ngOnDestroy(): void {
    if (this.mapView) {
      this.mapView.destroy();
    }
  }
}
