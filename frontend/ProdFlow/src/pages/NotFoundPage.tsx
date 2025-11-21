import React from "react";
import { Result } from "antd";
import { useNavigate } from "react-router-dom";
import ProdFlowButton from "../components/ui/Button";

const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Result
      status="404"
      title="404"
      subTitle="Страница не найдена"
      extra={
        <ProdFlowButton text="На главную" onClick={() => navigate("/")} />
      }
    />
  );
};

export default NotFoundPage;
