"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { getFeatures, getFeatureById, verifyFeature } from '@/lib/api';

const VerificationDashboard = () => {
  const [features, setFeatures] = useState([]);
  const [selectedFeature, setSelectedFeature] = useState(null);
  const [verificationResults, setVerificationResults] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  // Load features on component mount
  useEffect(() => {
    if (isAuthenticated) {
      fetchFeatures();
    }
  }, [isAuthenticated]);

  const fetchFeatures = async () => {
    try {
      setLoading(true);
      const data = await getFeatures();
      setFeatures(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyFeature = async (featureId) => {
    try {
      // Set status to in-progress
      setVerificationResults(prev => ({
        ...prev,
        [featureId]: { status: 'in_progress', message: 'Verification in progress...' }
      }));

      const result = await verifyFeature(featureId);

      setVerificationResults(prev => ({
        ...prev,
        [featureId]: {
          status: result.status,
          message: result.details || 'Verification completed',
          report: result
        }
      }));
    } catch (err) {
      setVerificationResults(prev => ({
        ...prev,
        [featureId]: {
          status: 'error',
          message: `Verification failed: ${err.message}`
        }
      }));
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'verified':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800';
      case 'pending':
        return 'bg-gray-100 text-gray-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'verified':
        return 'Verified';
      case 'failed':
        return 'Failed';
      case 'in_progress':
        return 'In Progress';
      case 'pending':
        return 'Pending';
      case 'error':
        return 'Error';
      default:
        return status;
    }
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading verification dashboard...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Redirect handled by useEffect
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Feature Verification Dashboard</h1>
          <p className="mt-2 text-gray-600">
            Monitor and verify all implemented features against original specifications
          </p>
        </div>

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Feature List */}
        <div className="bg-white shadow overflow-hidden sm:rounded-lg">
          <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
            <h2 className="text-lg leading-6 font-medium text-gray-900">Features</h2>
            <p className="mt-1 text-sm text-gray-500">
              List of all features with their verification status
            </p>
          </div>

          <ul className="divide-y divide-gray-200">
            {features.map((feature) => {
              const verificationResult = verificationResults[feature.id];
              const status = verificationResult?.status || 'pending';

              return (
                <li key={feature.id}>
                  <div className="px-4 py-5 sm:px-6">
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-medium text-gray-900 truncate">
                          {feature.name}
                        </h3>
                        <p className="mt-1 text-sm text-gray-500">
                          {feature.description}
                        </p>
                        <p className="mt-1 text-xs text-gray-400">
                          Specification: {feature.specification_reference}
                        </p>
                      </div>

                      <div className="ml-4 flex-shrink-0 flex items-center space-x-4">
                        {/* Status Badge */}
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(status)}`}>
                          {getStatusText(status)}
                        </span>

                        {/* Verify Button */}
                        <button
                          onClick={() => handleVerifyFeature(feature.id)}
                          disabled={status === 'in_progress'}
                          className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
                            status === 'in_progress'
                              ? 'bg-gray-400 cursor-not-allowed'
                              : 'bg-blue-600 hover:bg-blue-700'
                          }`}
                        >
                          {status === 'in_progress' ? 'Verifying...' : 'Verify'}
                        </button>
                      </div>
                    </div>

                    {/* Verification Details */}
                    {verificationResult && (
                      <div className="mt-4 pt-4 border-t border-gray-200">
                        <div className="text-sm">
                          <p className={`font-medium ${
                            verificationResult.status === 'verified' ? 'text-green-600' :
                            verificationResult.status === 'failed' ? 'text-red-600' :
                            verificationResult.status === 'error' ? 'text-red-600' :
                            'text-gray-600'
                          }`}>
                            {verificationResult.message}
                          </p>

                          {verificationResult.report && (
                            <div className="mt-2 text-xs text-gray-500">
                              <p>Completed at: {new Date(verificationResult.report.created_at).toLocaleString()}</p>
                              {verificationResult.report.issues_found && verificationResult.report.issues_found.length > 0 && (
                                <div className="mt-2">
                                  <p className="font-medium text-red-600">Issues Found:</p>
                                  <ul className="list-disc list-inside mt-1">
                                    {verificationResult.report.issues_found.map((issue, idx) => (
                                      <li key={idx} className="text-red-500">{issue}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </li>
              );
            })}
          </ul>
        </div>

        {/* Verification Summary */}
        {features.length > 0 && (
          <div className="mt-8 bg-white shadow overflow-hidden sm:rounded-lg">
            <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
              <h2 className="text-lg leading-6 font-medium text-gray-900">Verification Summary</h2>
            </div>

            <div className="px-4 py-5 sm:p-6">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-blue-50 rounded-lg p-4">
                  <div className="text-2xl font-bold text-blue-800">{features.length}</div>
                  <div className="text-sm text-blue-600">Total Features</div>
                </div>

                <div className="bg-green-50 rounded-lg p-4">
                  <div className="text-2xl font-bold text-green-800">
                    {Object.values(verificationResults).filter(r => r.status === 'verified').length}
                  </div>
                  <div className="text-sm text-green-600">Verified</div>
                </div>

                <div className="bg-red-50 rounded-lg p-4">
                  <div className="text-2xl font-bold text-red-800">
                    {Object.values(verificationResults).filter(r => r.status === 'failed').length}
                  </div>
                  <div className="text-sm text-red-600">Failed</div>
                </div>

                <div className="bg-yellow-50 rounded-lg p-4">
                  <div className="text-2xl font-bold text-yellow-800">
                    {Object.values(verificationResults).filter(r => r.status === 'in_progress').length}
                  </div>
                  <div className="text-sm text-yellow-600">In Progress</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VerificationDashboard;