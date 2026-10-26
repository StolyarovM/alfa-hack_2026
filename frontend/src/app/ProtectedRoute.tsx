
import { Navigate } from 'react-router-dom';
import { tokenExists } from '../api/auth';
export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  return tokenExists() ? <>{children}</> : <Navigate to="/login" replace />;
}
