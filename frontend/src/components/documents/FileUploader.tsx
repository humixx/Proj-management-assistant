'use client';

import { useCallback } from 'react';
import { useDocumentStore } from '@/lib/stores';

export default function FileUploader() {
  const { uploadDocument, uploadProgress, isUploading } = useDocumentStore();

  const handleFileChange = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;
    for (const file of Array.from(files)) {
      await uploadDocument(file);
    }
    e.target.value = '';
  }, [uploadDocument]);

  return (
    <div>
      <label className={`block border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${isUploading ? 'opacity-50' : 'hover:border-gray-400'}`}>
        <input
          type="file"
          onChange={handleFileChange}
          accept=".pdf,.docx"
          multiple
          disabled={isUploading}
          className="hidden"
        />
        <div className="text-gray-500">
          <p className="mb-1">Click to upload or drag and drop</p>
          <p className="text-sm text-gray-400">PDF and DOCX files</p>
        </div>
      </label>

      {Object.entries(uploadProgress).length > 0 && (
        <div className="mt-4 space-y-2">
          {Object.entries(uploadProgress).map(([filename, progress]) => (
            <div key={filename} className="bg-gray-50 rounded-lg p-3">
              <div className="flex justify-between text-sm mb-1">
                <span className="truncate">{filename}</span>
                <span>{progress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${progress}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
