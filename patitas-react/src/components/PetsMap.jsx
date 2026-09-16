import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Arreglo de iconos por defecto de Leaflet con Vite
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png';
import iconUrl from 'leaflet/dist/images/marker-icon.png';
import shadowUrl from 'leaflet/dist/images/marker-shadow.png';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({ iconRetinaUrl, iconUrl, shadowUrl });

function distanceMeters(lat1, lon1, lat2, lon2) {
  const toRad = (x) => (x * Math.PI) / 180;
  const R = 6378137;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

export default function PetsMap({ animales, especieLabels }) {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const markersRef = useRef([]);
  const userMarkerRef = useRef(null);
  const circleRef = useRef(null);

  useEffect(() => {
    if (!mapRef.current || mapInstance.current) return;

    const map = L.map(mapRef.current).setView([4.6097, -74.0817], 11);
    mapInstance.current = map;

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);

    map.whenReady(() => {
      setTimeout(() => map.invalidateSize(), 250);
    });

    return () => {
      map.remove();
      mapInstance.current = null;
    };
  }, []);

  function clearMarkers() {
    markersRef.current.forEach((m) => mapInstance.current.removeLayer(m));
    markersRef.current = [];
    if (circleRef.current) {
      mapInstance.current.removeLayer(circleRef.current);
      circleRef.current = null;
    }
  }

  function showNearby(lat, lng) {
    const map = mapInstance.current;
    clearMarkers();
    circleRef.current = L.circle([lat, lng], {
      radius: 1000,
      color: '#8C5E3C',
      fillOpacity: 0.05,
    }).addTo(map);

    animales.forEach((a) => {
      if (a.latitud == null || a.longitud == null) return;
      const d = distanceMeters(lat, lng, a.latitud, a.longitud);
      if (d <= 1000) {
        const marker = L.marker([a.latitud, a.longitud], {
          icon: L.divIcon({
            className: 'location-marker',
            html: '<i class="fas fa-paw"></i>',
            iconSize: [30, 30],
          }),
        }).addTo(map);
        const popupHtml = `
          <div class="map-popup">
            <img src="${a.foto_url || '/images/paw-placeholder.svg'}" alt="${a.nombre || ''}" />
            <h3>${a.nombre || 'Sin nombre'}</h3>
            <p>${a.especie_display || especieLabels[a.especie] || a.especie} ${a.edad ? '· ' + a.edad + ' años' : ''}</p>
            <p>${(a.descripcion || '').slice(0, 50)}</p>
          </div>`;
        marker.bindPopup(popupHtml);
        markersRef.current.push(marker);
      }
    });
  }

  function handleLocate() {
    if (!navigator.geolocation) {
      alert('Geolocalización no soportada por el navegador.');
      return;
    }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude: lat, longitude: lng } = pos.coords;
        if (userMarkerRef.current) mapInstance.current.removeLayer(userMarkerRef.current);
        userMarkerRef.current = L.marker([lat, lng], { title: 'Tu ubicación' }).addTo(
          mapInstance.current
        );
        mapInstance.current.setView([lat, lng], 14);
        showNearby(lat, lng);
      },
      (err) => {
        console.warn(err);
        alert('No se pudo obtener la ubicación. Asegúrate de permitir el acceso.');
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }

  return (
    <div className="map-container" style={{ position: 'relative' }}>
      <div id="map" ref={mapRef}></div>
      <button
        id="locate-btn"
        className="btn"
        style={{ position: 'absolute', top: 16, right: 16, zIndex: 1200 }}
        onClick={handleLocate}
      >
        Localizarme
      </button>
    </div>
  );
}
