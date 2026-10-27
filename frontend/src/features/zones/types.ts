export interface Zone {
  id: string;
  camera_id: string;
  name: string;
  polygon_coordinates: [number, number][]; // normalized 0-1 [x, y] pairs
}
