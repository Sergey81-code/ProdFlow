import './App.css';

import { Layout } from 'antd';
import React, { useState } from 'react';
import { Route,Routes } from 'react-router-dom';

import ProtectedRoute from './components/auth/ProtectedRoute';
import { LogsModal } from './components/modals/LogModal';
import PageFooter from './components/ui/PageFooter';
import PageHeader from './components/ui/PageHeader';
import AdminPage from './pages/AdminPage';
import LoginPage from './pages/LoginPage';
import NotFoundPage from './pages/NotFoundPage';

const { Content } = Layout;

const App: React.FC = () => {
  const [logsModalVisible, setLogsModalVisible] = useState(false);

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <PageHeader />
      <Content style={{ padding: 24 }}>
        <Routes>
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <AdminPage />
              </ProtectedRoute>
            }
          />
          <Route path="/login" element={<LoginPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Content>

      <PageFooter onShowLogs={() => setLogsModalVisible(true)} />

      <LogsModal
        visible={logsModalVisible}
        onClose={() => setLogsModalVisible(false)}
      />
    </Layout>
  );
};

export default App;
