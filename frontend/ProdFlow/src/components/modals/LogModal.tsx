import React, { useEffect, useState } from "react";
import { Modal, List, Button, message, Spin, Tag } from "antd";
import { DownloadOutlined, FileTextOutlined } from "@ant-design/icons";
import { getLogs, getLogFile } from "../../api/index";
import Editor from "@monaco-editor/react";


interface Props {
  visible: boolean;
  onClose: () => void;
}

const LAST_LINES = 20;
const LAST_BYTES = 512 * 1024;

export const LogsModal: React.FC<Props> = ({ visible, onClose }) => {
  const [logs, setLogs] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedLog, setSelectedLog] = useState<string | null>(null);
  const [logContent, setLogContent] = useState<string>("");
  const [loadingContent, setLoadingContent] = useState(false);
  const [fileBlob, setFileBlob] = useState<Blob | null>(null);
  const [viewMode, setViewMode] = useState<"full" | "last">("full");

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const data = await getLogs();
      setLogs(data.logs || []);
    } catch (err: any) {
      message.error(err?.message || "Ошибка при загрузке логов");
    } finally {
      setLoading(false);
    }
  };

  const fetchLogContent = async (filename: string) => {
    setSelectedLog(filename);
    setViewMode("full");
    setLoadingContent(true);
    try {
      const blob = await getLogFile(filename);
      setFileBlob(blob);
      const text = await blob.text();
      setLogContent(text);
    } catch (err: any) {
      message.error(err?.message || "Ошибка при открытии файла лога");
    } finally {
      setLoadingContent(false);
    }
  };

  const openLastPart = async (filename: string) => {
    setSelectedLog(filename);
    setViewMode("last");
    setLoadingContent(true);
    try {
      const blob = await getLogFile(filename);
      const size = blob.size;
      const sliced = size > LAST_BYTES ? blob.slice(size - LAST_BYTES, size) : blob;
      const text = await sliced.text();
      const lines = text.split("\n");
      const lastPart =
        lines.length > LAST_LINES ? lines.slice(-LAST_LINES).join("\n") : text;

      setFileBlob(blob);
      setLogContent(lastPart);
    } catch (err: any) {
      message.error(err?.message || "Ошибка при чтении файла");
    } finally {
      setLoadingContent(false);
    }
  };

  const downloadCurrentFile = () => {
    if (!fileBlob || !selectedLog) return;
    const url = URL.createObjectURL(fileBlob);
    const a = document.createElement("a");
    a.href = url;
    a.download = selectedLog;
    a.click();
    URL.revokeObjectURL(url);
  };

  useEffect(() => {
    if (visible) {
      fetchLogs();
      setSelectedLog(null);
      setFileBlob(null);
      setLogContent("");
    }
  }, [visible]);

  return (
    <Modal
      open={visible}
      onCancel={onClose}
      footer={null}
      width="90%"
      style={{ top: 20 }}
      title={null}
      closable={false}
      styles={{ body: { padding: 0, background: "transparent", overflow: "hidden" } }}
      centered
    >
      <div
        style={{
          background: "linear-gradient(90deg, #FFD8A8 0%, #FFB347 100%)",
          padding: "16px 24px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          borderBottom: "1px solid #eee",
          borderTopLeftRadius: 8,
          borderTopRightRadius: 8,
          flexWrap: "wrap",
          gap: 8,
        }}
      >
        <div style={{ fontSize: 18, fontWeight: 600, color: "#333", flex: 1, minWidth: 0 }}>
          {selectedLog ? (
            <>
              {selectedLog}
              {viewMode === "last" && (
                <Tag color="orange" style={{ marginLeft: 10 }}>
                  последние записи
                </Tag>
              )}
            </>
          ) : (
            "Список логов"
          )}
        </div>

        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {selectedLog && (
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              onClick={downloadCurrentFile}
              style={{color: "#000", background: "#fff"}}
            >
            Скачать
            </Button>
          )}
          <Button
            onClick={selectedLog ? () => setSelectedLog(null) : onClose}
            style={{ fontSize: 18, padding: "0 8px", lineHeight: 1 }}
          >
            ×
          </Button>
        </div>
      </div>

      <div style={{ padding: 24 }}>
        {!selectedLog ? (
          loading ? (
            <div style={{ textAlign: "center", padding: 50 }}>
              <Spin size="large" />
            </div>
          ) : (
            <List
              dataSource={logs}
              renderItem={(item) => (
                <List.Item
                  style={{
                    width: "100%",
                    display: "flex",
                    flexDirection: "column",
                    justifyContent: "space-between",
                    alignItems: "stretch",
                    padding: "12px 16px",
                    borderRadius: 8,
                    background: "#fff",
                    boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
                    marginBottom: 12,
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
                    <FileTextOutlined style={{ fontSize: 20, color: "#FF8A00" }} />
                    <strong>{item}</strong>
                  </div>
                  <div
                    style={{
                      display: "flex",
                      gap: 8,
                      flexWrap: "wrap",
                      marginTop: 8,
                    }}
                  >
                    <Button
                      type="primary"
                      style={{ flex: 1, minWidth: 140, background: "#ffb348", color: "rgb(247 244 244)" }}
                      onClick={() => fetchLogContent(item)}
                    >
                      Открыть полностью
                    </Button>
                    <Button
                      style={{ flex: 1, minWidth: 140 }}
                      onClick={() => openLastPart(item)}
                    >
                      Последние записи
                    </Button>
                  </div>
                </List.Item>
              )}
            />
          )
        ) : loadingContent ? (
          <div style={{ textAlign: "center", padding: 50 }}>
            <Spin size="large" />
          </div>
        ) : (
          <Editor
            height="65vh"
            defaultLanguage="plaintext"
            value={logContent}
            options={{
              readOnly: true,
              minimap: { enabled: false },
              lineNumbers: "on",
              scrollBeyondLastLine: false,
              wordWrap: "on",
            }}
          />
        )}
      </div>
    </Modal>
  );
};
