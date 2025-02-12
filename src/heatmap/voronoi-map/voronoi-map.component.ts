import { Component, AfterViewInit, OnDestroy } from '@angular/core';
import WebMap from '@arcgis/core/WebMap';
import MapView from '@arcgis/core/views/MapView';
import FeatureLayer from '@arcgis/core/layers/FeatureLayer';
import Graphic from '@arcgis/core/Graphic';
import Polygon from '@arcgis/core/geometry/Polygon';
import Point from '@arcgis/core/geometry/Point';
import Basemap from '@arcgis/core/Basemap';
import { zipCodeData } from '../../assets/data/ZipCodeData'; // Your zip code data
import { voronoi } from 'd3-voronoi'; // Use d3-voronoi to generate the polygons
import Color from '@arcgis/core/Color';
import UniqueValueRenderer from '@arcgis/core/renderers/UniqueValueRenderer';
import Field from '@arcgis/core/layers/support/Field';

@Component({
  selector: 'app-voronoi-map',
  standalone: true,
  imports: [],
  templateUrl: './voronoi-map.component.html',
  styleUrl: './voronoi-map.component.css',
})
export class VoronoiMapComponent implements AfterViewInit, OnDestroy {
  private mapView!: MapView;
  featureLayer!: FeatureLayer;
  baseMap = 'streets';

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
      container: 'voronoiView',
      map: webmap,
      zoom: 4,
      center: [-117.201757, 34.872701],
    });

    // Generate Voronoi polygons
    const voronoiPolygons = this.generateVoronoiPolygons();

    this.featureLayer = new FeatureLayer({
      source: voronoiPolygons,
      objectIdField: 'ObjectID',
      geometryType: 'polygon',
      spatialReference: { wkid: 4326 },
      fields: [
        { name: 'ObjectID', alias: 'ObjectID', type: 'oid' },
        { name: 'Zip_Code', alias: 'Zip Code', type: 'string' },
        { name: 'Count', alias: 'Student Count', type: 'integer' },
      ],
      popupTemplate: {
        title: 'Zip Code: {Zip_Code}',
        content: 'Student Count: {Count}',
      },
      renderer: this.createVoronoiRenderer(),
    });

    webmap.add(this.featureLayer);
  }

  generateVoronoiPolygons(): Graphic[] {
    const points: [number, number][] = zipCodeData
  .filter(entry => entry.LNG !== null && entry.LAT !== null)
  .map(entry => [entry.LNG as number, entry.LAT as number]); // Ensure tuples

  // Calculate bounding box for the data points
  const minLng = Math.min(...points.map(([lng]) => lng));
  const maxLng = Math.max(...points.map(([lng]) => lng));
  const minLat = Math.min(...points.map(([, lat]) => lat));
  const maxLat = Math.max(...points.map(([, lat]) => lat));

const voronoiDiagram = voronoi()
  .extent([[minLng, minLat], [maxLng, maxLat]]) // Define bounding box
  .polygons(points);

    return voronoiDiagram.map((polygon: number[][], index: number) => {
      return new Graphic({
        geometry: new Polygon({
          rings: [polygon],
          spatialReference: { wkid: 4326 },
        }),
        attributes: {
          ObjectID: index,
          Zip_Code: zipCodeData[index].Zip_Code,
          Count: zipCodeData[index].Count,
        },
      });
    });
  }

  createVoronoiRenderer(): UniqueValueRenderer {
    return new UniqueValueRenderer({
      field: 'Zip_Code',
      uniqueValueInfos: zipCodeData.map((entry) => ({
        value: entry.Zip_Code,
        symbol: {
          type: 'simple-fill',
          color: new Color([Math.random() * 255, Math.random() * 255, Math.random() * 255, 0.5]),
          outline: {
            color: 'black',
            width: 1,
          },
        },
      })),
    });
  }

  updateBasemap(): void {
    this.mapView.map.basemap = Basemap.fromId(this.baseMap);
  }

  ngOnDestroy(): void {
    if (this.mapView) {
      this.mapView.destroy();
    }
  }
}
