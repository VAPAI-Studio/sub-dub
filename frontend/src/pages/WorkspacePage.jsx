import { useState, useRef, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { transcribe as apiTranscribe, uploadProjectAudio, getProjectAudioUrl, getProjectDubUrl } from "../api";
import { getVoices } from "../api";
import { useProject } from "../hooks/useProject";
import UploadPanel from "../components/UploadPanel";
import OptionsPanel from "../components/OptionsPanel";
import TranscriptionResult from "../components/TranscriptionResult";
import TranslatePanel from "../components/TranslatePanel";
import DubPanel from "../components/DubPanel";
import LanguageTabs from "../components/LanguageTabs";
import "../App.css";

function WorkspacePage() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { project, loading: projectLoading } = useProject(projectId);

  const [file, setFile] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [audioFilename, setAudioFilename] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [translations, setTranslations] = useState({});
  const [dubs, setDubs] = useState({});
  const [activeLanguage, setActiveLanguage] = useState(null);
  const [showAddLanguage, setShowAddLanguage] = useState(false);
  const [voices, setVoices] = useState([]);
  const [uploading, setUploading] = useState(false);
  const audioRef = useRef(null);

  const [options, setOptions] = useState({
    modelSize: "large-v2",
    language: "auto",
    task: "transcribe",
    align: false,
    diarize: false,
    minSpeakers: "",
    maxSpeakers: "",
  });

  useEffect(() => {
    getVoices()
      .then(setVoices)
      .catch(() => {});
  }, []);

  // Load project data when available
  useEffect(() => {
    if (project) {
      if (project.audio_file) {
        setAudioUrl(getProjectAudioUrl(project.id));
        setAudioFilename(project.audio_file.original_filename);
      }
      if (project.transcription) {
        setResult({
          segments: project.transcription.segments_json,
          language: project.transcription.language,
        });
      }
      if (project.translations?.length) {
        const map = {};
        for (const t of project.translations) {
          map[t.target_language] = { segments: t.segments_json, language: t.target_language };
        }
        setTranslations(map);
        setActiveLanguage(project.translations[0].target_language);
      }
      if (project.dubs?.length) {
        const map = {};
        for (const d of project.dubs) {
          map[d.target_language] = getProjectDubUrl(project.id, d.target_language);
        }
        setDubs(map);
      }
    }
  }, [project]);

  const handleFileChange = async (e) => {
    const selected = e.target.files[0] || null;
    setFile(selected);
    setResult(null);
    setError(null);
    setTranslations({});
    setDubs({});
    setActiveLanguage(null);
    if (audioUrl && audioUrl.startsWith('blob:')) URL.revokeObjectURL(audioUrl);
    setAudioUrl(selected ? URL.createObjectURL(selected) : null);
    setAudioFilename(selected ? selected.name : null);

    if (selected && projectId) {
      setUploading(true);
      try {
        await uploadProjectAudio(projectId, selected);
      } catch (err) {
        console.error('Error uploading audio:', err);
      } finally {
        setUploading(false);
      }
    }
  };

  const handleSegmentClick = (startTime) => {
    if (audioRef.current) {
      audioRef.current.currentTime = startTime;
      audioRef.current.play();
    }
  };

  const handleUpdateSegment = (index, field, value) => {
    setResult((prev) => {
      const segments = prev.segments.map((seg, i) =>
        i === index ? { ...seg, [field]: value } : seg,
      );
      return { ...prev, segments };
    });
  };

  const handleTranscribe = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setTranslations({});
    setDubs({});
    setActiveLanguage(null);

    try {
      const data = await apiTranscribe(file, options, projectId);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTranslated = (data) => {
    setTranslations(prev => ({ ...prev, [data.language]: data }));
    setActiveLanguage(data.language);
    setShowAddLanguage(false);
  };

  const handleDubCreated = (language, blobUrl) => {
    setDubs(prev => ({ ...prev, [language]: blobUrl }));
  };

  if (projectLoading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-black border-t-transparent"></div>
          <p className="mt-4 text-gray-500">Cargando proyecto...</p>
        </div>
      </div>
    );
  }

  const languageKeys = Object.keys(translations);
  const activeTranslation = activeLanguage ? translations[activeLanguage] : null;

  return (
    <div className="min-h-screen bg-white">
      {/* Editorial Header with Back Button */}
      <header className="border-b-4 border-black px-8 py-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-between">
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-2 text-gray-600 hover:text-black transition-colors group"
            >
              <svg className="w-5 h-5 transform group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span className="font-semibold">Proyectos</span>
            </button>
            {project && (
              <div className="text-center flex-1">
                <h1 className="text-3xl font-black">{project.name}</h1>
                <p className="text-sm text-gray-500 font-mono mt-1">ID: {project.id.slice(0, 8)}</p>
              </div>
            )}
            <div className="w-24"></div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-8 py-8">
        <div className="app">
          <UploadPanel
            file={file}
            audioUrl={audioUrl}
            audioRef={audioRef}
            onFileChange={handleFileChange}
            audioFilename={audioFilename}
            uploading={uploading}
          />

          <OptionsPanel options={options} onChange={setOptions} />

          <button
            onClick={handleTranscribe}
            disabled={(!file && !audioUrl) || loading}
            className="transcribe-btn"
          >
            {loading ? "Procesando..." : "Transcribir"}
          </button>

          {loading && (
            <div className="loading">
              <div className="spinner" />
              <p>Procesando audio... esto puede tardar unos segundos.</p>
            </div>
          )}

          {error && <p className="error">{error}</p>}

          {result && (
            <TranscriptionResult
              result={result}
              onUpdateSegment={handleUpdateSegment}
              onSegmentClick={handleSegmentClick}
            />
          )}

          {result && (
            <>
              {languageKeys.length > 0 && (
                <LanguageTabs
                  languages={languageKeys}
                  activeLanguage={activeLanguage}
                  onSelectLanguage={(lang) => { setActiveLanguage(lang); setShowAddLanguage(false); }}
                  onAddLanguage={() => setShowAddLanguage(true)}
                  dubLanguages={Object.keys(dubs)}
                />
              )}

              <TranslatePanel
                result={result}
                activeTranslation={activeTranslation}
                onTranslated={handleTranslated}
                onSegmentClick={handleSegmentClick}
                projectId={projectId}
                existingLanguages={languageKeys}
                showAddForm={showAddLanguage || languageKeys.length === 0}
              />

              {activeLanguage && activeTranslation && voices.length > 0 && (
                <DubPanel
                  key={activeLanguage}
                  translated={activeTranslation}
                  voices={voices}
                  projectId={projectId}
                  result={result}
                  existingDubUrl={dubs[activeLanguage] || null}
                  onDubCreated={handleDubCreated}
                />
              )}
            </>
          )}
        </div>
      </main>
    </div>
  );
}

export default WorkspacePage;
