import { useState } from "react";
import api from "../services/api";

export default function UploadSection() {

  const [files,setFiles] = useState([]);

  const handleChange = (e) => {
      setFiles(
          [...e.target.files]
      );
  };

  const upload = async () => {

      const formData =
          new FormData();

      files.forEach(file => {
          formData.append(
              "files",
              file
          );
      });

      const response =
          await api.post(
              "/vectorize",
              formData,
              {
                  responseType:
                      "blob"
              }
          );

      const url =
          window.URL.createObjectURL(
              response.data
          );

      const link =
          document.createElement("a");

      link.href = url;

      link.download =
          files.length > 1
          ? "vectors.zip"
          : "vector.svg";

      link.click();
  };

  return (
      <div className="container">

          <input
              type="file"
              multiple
              onChange={handleChange}
          />

          <button
              onClick={upload}
          >
              Convertir
          </button>

      </div>
  );
}