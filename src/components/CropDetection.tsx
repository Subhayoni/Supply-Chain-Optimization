import React, { useEffect, useState } from 'react';
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react';

interface CropDetectionProps {
  image: string | null;
  onDetectionComplete: (result: DetectionResult) => void;
}

export interface DetectionResult {
  cropType: string;
  variety: string;
  confidence: number;
  characteristics: string[];
}

const CropDetection: React.FC<CropDetectionProps> = ({ image, onDetectionComplete }) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<DetectionResult | null>(null);

  // Simulated AI detection - in production, this would call a real ML API
  const simulateDetection = async (): Promise<DetectionResult> => {
    const crops = [
      {
        cropType: 'Rice',
        variety: 'Basmati',
        confidence: 92,
        characteristics: ['Long grain', 'Aromatic', 'Premium quality', 'White color']
      },
      {
        cropType: 'Rice',
        variety: 'Jasmine',
        confidence: 88,
        characteristics: ['Medium grain', 'Fragrant', 'Soft texture', 'Slightly sticky']
      },
      {
        cropType: 'Wheat',
        variety: 'Durum',
        confidence: 85,
        characteristics: ['Hard wheat', 'High protein', 'Golden color', 'Premium grade']
      },
      {
        cropType: 'Wheat',
        variety: 'Soft Red Winter',
        confidence: 90,
        characteristics: ['Soft wheat', 'Low protein', 'Good for pastry', 'Reddish tint']
      },
      {
        cropType: 'Paddy',
        variety: 'Long Grain',
        confidence: 87,
        characteristics: ['Unhusked rice', 'Brown outer layer', 'Raw form', 'Field harvested']
      }
    ];

    return crops[Math.floor(Math.random() * crops.length)];
  };

  useEffect(() => {
    if (image) {
      setIsAnalyzing(true);
      setResult(null);

      // Simulate processing time
      setTimeout(async () => {
        const detectionResult = await simulateDetection();
        setResult(detectionResult);
        setIsAnalyzing(false);
        onDetectionComplete(detectionResult);
      }, 2500);
    }
  }, [image, onDetectionComplete]);

  if (!image) return null;

  return (
    <div className="w-full max-w-2xl mx-auto mt-6">
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
          {isAnalyzing ? (
            <>
              <Loader2 className="w-5 h-5 text-blue-500 animate-spin mr-2" />
              Analyzing Crop...
            </>
          ) : result ? (
            <>
              <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
              Detection Complete
            </>
          ) : (
            <>
              <AlertCircle className="w-5 h-5 text-yellow-500 mr-2" />
              Ready to Analyze
            </>
          )}
        </h3>

        {isAnalyzing && (
          <div className="text-center py-8">
            <div className="inline-flex items-center space-x-2 text-gray-600">
              <Loader2 className="w-6 h-6 animate-spin" />
              <span>Processing image with AI...</span>
            </div>
            <div className="mt-4 text-sm text-gray-500">
              Identifying crop type and variety
            </div>
          </div>
        )}

        {result && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium text-gray-500">Crop Type</label>
                <div className="text-lg font-semibold text-gray-800">{result.cropType}</div>
              </div>
              <div>
                <label className="text-sm font-medium text-gray-500">Variety</label>
                <div className="text-lg font-semibold text-gray-800">{result.variety}</div>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-500">Confidence</label>
              <div className="flex items-center space-x-2 mt-1">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-green-500 h-2 rounded-full transition-all duration-500"
                    style={{ width: `${result.confidence}%` }}
                  ></div>
                </div>
                <span className="text-sm font-semibold text-gray-700">{result.confidence}%</span>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-gray-500 mb-2 block">Characteristics</label>
              <div className="flex flex-wrap gap-2">
                {result.characteristics.map((char, index) => (
                  <span 
                    key={index}
                    className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm"
                  >
                    {char}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CropDetection;