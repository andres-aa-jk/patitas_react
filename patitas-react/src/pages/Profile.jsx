import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Profile() {
  const { user } = useAuth();

  return (
    <center>
      <div className="empty-state" style={{ maxWidth: 800 }}>
        <h2>Mi perfil</h2>
        <div
          style={{
            background: 'white',
            padding: '1.5rem',
            borderRadius: 12,
            marginTop: '1rem',
            boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
            width: '100%',
          }}
        >
          <p>
            <strong>Usuario:</strong> {user?.username}
          </p>
          <p>
            <strong>Email:</strong> {user?.email}
          </p>
          {user?.direccion && (
            <p>
              <strong>Dirección:</strong> {user.direccion}
            </p>
          )}
          {user?.numero && (
            <p>
              <strong>Teléfono:</strong> {user.numero}
            </p>
          )}
        </div>
        <div style={{ marginTop: '1rem' }}>
          <Link to="/perfil/editar" className="btn">
            Editar perfil
          </Link>
        </div>
      </div>
    </center>
  );
}
