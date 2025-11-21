import React, { useState } from "react";
import { Layout } from "antd";
import { Routes, Route } from "react-router-dom";
import AdminPage from "./pages/AdminPage";
import NotFoundPage from "./pages/NotFoundPage";
import PageHeader from "./components/ui/PageHeader";
import PageFooter from "./components/ui/PageFooter";
import ProtectedRoute from "./components/auth/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import { LogsModal } from "./components/modals/LogModal";

import "./App.css";

const { Content } = Layout;

const App: React.FC = () => {
  const [logsModalVisible, setLogsModalVisible] = useState(false);

  return (
    <Layout style={{ minHeight: "100vh" }}>
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
