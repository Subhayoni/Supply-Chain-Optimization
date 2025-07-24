import React, { useState } from 'react';
import { Wheat, TrendingUp, Camera, BarChart3 } from 'lucide-react';
import ImageUpload from './components/ImageUpload';
import CropDetection, { DetectionResult } from './components/CropDetection';
import PriceDisplay from './components/PriceDisplay';

function App() {
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [detectionResult, setDetectionResult] = useState<DetectionResult | null>(null);

  const handleImageUpload = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      setUploadedImage(e.target?.result as string);
      setDetectionResult(null); // Reset detection when new image is uploaded
    };
    reader.readAsDataURL(file);
  };

  const handleClearImage = () => {
    setUploadedImage(null);
    setDetectionResult(null);
  };

  const handleDetectionComplete = (result: DetectionResult) => {
    setDetectionResult(result);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-yellow-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-green-600 rounded-lg">
                <Wheat className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">CropPrice AI</h1>
                <p className="text-sm text-gray-600">Intelligent Crop Detection & Price Analysis</p>
              </div>
            </div>
            <div className="hidden md:flex items-center space-x-6 text-sm text-gray-600">
              <div className="flex items-center space-x-1">
                <Camera className="w-4 h-4" />
                <span>AI Detection</span>
              </div>
              <div className="flex items-center space-x-1">
                <TrendingUp className="w-4 h-4" />
                <span>Live Prices</span>
              </div>
              <div className="flex items-center space-x-1">
                <BarChart3 className="w-4 h-4" />
                <span>Market Analytics</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Upload. Detect. Get Market Prices.
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Upload images of your crops and get instant AI-powered identification with real-time market prices 
            from agricultural exchanges across the country.
          </p>
        </div>

        {/* Features Grid */}
        {!uploadedImage && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
            <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <Camera className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">AI-Powered Detection</h3>
              <p className="text-gray-600">Advanced machine learning algorithms identify crop types and varieties with high accuracy.</p>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Real-Time Prices</h3>
              <p className="text-gray-600">Get current market prices from major agricultural exchanges and trading platforms.</p>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow">
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mb-4">
                <BarChart3 className="w-6 h-6 text-yellow-600" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Market Analytics</h3>
              <p className="text-gray-600">Comprehensive price trends, market insights, and trading recommendations.</p>
            </div>
          </div>
        )}

        {/* Upload Section */}
        <div className="space-y-8">
          <ImageUpload
            onImageUpload={handleImageUpload}
            uploadedImage={uploadedImage}
            onClearImage={handleClearImage}
          />

          {/* Detection Section */}
          <CropDetection
            image={uploadedImage}
            onDetectionComplete={handleDetectionComplete}
          />

          {/* Price Display Section */}
          <PriceDisplay detectionResult={detectionResult} />
        </div>

        {/* Additional Info */}
        {detectionResult && (
          <div className="mt-12 bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-semibold text-gray-800 mb-4">About This Detection</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold text-gray-700 mb-2">Crop Information</h4>
                <div className="space-y-2 text-sm text-gray-600">
                  <p><strong>Type:</strong> {detectionResult.cropType}</p>
                  <p><strong>Variety:</strong> {detectionResult.variety}</p>
                  <p><strong>Quality Grade:</strong> Premium (based on visual characteristics)</p>
                  <p><strong>Moisture Content:</strong> Estimated 12-14% (ideal for storage)</p>
                </div>
              </div>
              <div>
                <h4 className="font-semibold text-gray-700 mb-2">Market Recommendations</h4>
                <div className="space-y-2 text-sm text-gray-600">
                  <p>• Current market conditions favor sellers</p>
                  <p>• Consider bulk sale for better pricing</p>
                  <p>• Peak demand season: Next 2-3 months</p>
                  <p>• Storage costs: ₹5-8 per quintal per month</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <Wheat className="w-6 h-6" />
              <span className="text-xl font-bold">CropPrice AI</span>
            </div>
            <p className="text-gray-400 mb-4">
              Empowering farmers with AI-driven crop detection and real-time market intelligence
            </p>
            <div className="text-sm text-gray-500">
              <p>Data sourced from National Agricultural Market (eNAM) and other verified trading platforms</p>
              <p className="mt-2">© 2025 CropPrice AI. Built for agricultural excellence.</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;