import React from 'react';
import { useAppStore } from '../store'; // Import the Zustand store
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

// Props are no longer needed as state comes from the store
// interface ArtifactWindowProps {
//   content: ArtifactContentType;
//   isVisible: boolean;
//   onClose: () => void;
// }

const ArtifactWindow: React.FC = () => {
  const { artifactContent, isArtifactVisible, closeArtifact } = useAppStore(state => ({
    artifactContent: state.artifactContent,
    isArtifactVisible: state.isArtifactVisible,
    closeArtifact: state.closeArtifact,
  }));

  if (!isArtifactVisible || !artifactContent) { // Ensure artifactContent is not null
    return null;
  }

  const renderContent = () => {
    if (typeof artifactContent === 'string') {
      return <div className="whitespace-pre-wrap text-sm p-2">{artifactContent}</div>;
    }

    // Type guards for structured content
    if (artifactContent && typeof artifactContent === 'object') {
      switch (artifactContent.type) {
        case 'code':
          return (
            <div className="text-sm">
              {artifactContent.language && <p className="text-xs text-gray-400 mb-1 px-2 pt-1">Language: {artifactContent.language}</p>}
              <SyntaxHighlighter 
                language={artifactContent.language || 'plaintext'} 
                style={atomDark} 
                customStyle={{ margin: 0, borderRadius: "0 0 0.5rem 0.5rem", padding: "1rem"}}
                wrapLongLines={true}
              >
                {String(artifactContent.content)}
              </SyntaxHighlighter>
            </div>
          );
        case 'data':
          // Ensure content.content exists and has the expected structure
          if (artifactContent.content && 
              typeof artifactContent.content === 'object' && // Check if content is an object
              'columns' in artifactContent.content && Array.isArray(artifactContent.content.columns) && 
              'rows' in artifactContent.content && Array.isArray(artifactContent.content.rows)) {
            const tableData = artifactContent.content; // Already checked it's not null
            const tableTitle = tableData.title || "Data Table";
            return (
              <div className="overflow-x-auto p-1">
                <h3 className="text-md font-semibold text-gray-700 mb-2 px-1">{tableTitle}</h3>
                <table className="min-w-full divide-y divide-gray-300 border border-gray-300 shadow-sm rounded-md">
                  <thead className="bg-gray-200">
                    <tr>
                      {tableData.columns.map((col: string, index: number) => (
                        <th 
                          key={index} 
                          scope="col"
                          className="px-4 py-2.5 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider border-r border-gray-300 last:border-r-0"
                        >
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {tableData.rows.map((row: any[], rowIndex: number) => (
                      <tr key={rowIndex} className={rowIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50 hover:bg-gray-100'}>
                        {row.map((cell: any, cellIndex: number) => (
                          <td 
                            key={cellIndex} 
                            className="px-4 py-2 whitespace-nowrap text-sm text-gray-700 border-r border-gray-200 last:border-r-0"
                          >
                            {String(cell)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            );
          }
          return <div className="whitespace-pre-wrap text-sm p-2">Invalid data format for table.</div>;
        case 'message':
          return <div className="whitespace-pre-wrap text-sm p-2">{String(artifactContent.content)}</div>;
        default:
          return <pre className="whitespace-pre-wrap text-sm bg-gray-100 p-2 rounded-md">{JSON.stringify(artifactContent, null, 2)}</pre>;
      }
    }
    return <div className="text-sm p-2">Unable to display artifact content.</div>;
  };

  return (
    <div className="h-full border border-gray-300 rounded-lg shadow-xl bg-white flex flex-col">
      <div className="flex justify-between items-center p-3 bg-gray-200 border-b border-gray-300 rounded-t-lg">
        <h2 className="text-lg font-semibold text-gray-800">Artifact Viewer</h2>
        <button 
          onClick={closeArtifact} // Use action from store
          className="p-1.5 text-gray-600 hover:text-gray-800 hover:bg-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-gray-400 transition-colors"
          aria-label="Close artifact viewer"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      <div className="flex-grow overflow-y-auto">
        {renderContent()}
      </div>
    </div>
  );
};

export default ArtifactWindow;
