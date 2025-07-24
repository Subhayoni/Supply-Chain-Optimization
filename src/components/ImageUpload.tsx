import React, { useState, useRef } from 'react';
import { Upload, Camera, X } from 'lucide-react';

interface ImageUploadProps {
  onImageUpload: (file: File) => void;
  uploadedImage: string | null;
  onClearImage: () => void;
}

const ImageUpload: React.FC<ImageUploadProps> = ({ onImageUpload, uploadedImage, onClearImage }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.type.startsWith('image/')) {
        onImageUpload(file);
      }
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      onImageUpload(files[0]);
    }
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      {!uploadedImage ? (
        <div
          className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 cursor-pointer
            ${isDragOver 
              ? 'border-green-500 bg-green-50 scale-105' 
              : 'border-gray-300 hover:border-green-400 hover:bg-gray-50'
            }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={openFileDialog}
        >
          <div className="flex flex-col items-center space-y-4">
            <div className="p-4 rounded-full bg-green-100">
              <Upload className="w-8 h-8 text-green-600" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-700 mb-2">Upload Crop Image</h3>
              <p className="text-gray-500 mb-4">
                Drag and drop your image here, or click to select
              </p>
              <p className="text-sm text-gray-400">
                Supports: Paddy, Wheat, Rice varieties
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <button className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                <Camera className="w-4 h-4" />
                <span>Choose File</span>
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="relative rounded-xl overflow-hidden shadow-lg">
          <img
            src={uploadedImage}
            alt="Uploaded crop"
            className="w-full h-64 object-cover"
          />
          <button
            onClick={onClearImage}
            className="absolute top-4 right-4 p-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
      
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        className="hidden"
      />
    </div>
  );
};

export default ImageUpload;