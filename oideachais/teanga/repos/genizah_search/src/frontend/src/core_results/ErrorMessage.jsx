import React from 'react';

const ErrorMessage = ({ error, onDismiss }) => (
    <div className="mb-6 rounded-xl p-4 bg-orange-50 border border-orange-200">
        <div className="flex justify-between items-start">
            <div>
                <h4 className="font-medium text-orange-800">
                    Error
                </h4>
                <p className="mt-1 text-orange-700">
                    {error.message}
                </p>
            </div>
            <button
                onClick={onDismiss}
                className="text-sm px-3 py-1 rounded-md bg-orange-100 text-orange-800 hover:bg-orange-200"
            >
                Dismiss
            </button>
        </div>
    </div>
);

export default ErrorMessage;
// document message