import ProviderSettings from '@/components/ProviderSettings';

const PROVIDERS = ['SARVAM', 'ELEVENLABS'];

export default function STTProviderPage() {
  return (
    <ProviderSettings 
      titlePrefix="Speech-to-Text"
      titleHighlight="Providers"
      description="Configure your API keys and models for STT services securely."
      providers={PROVIDERS}
      theme="accent"
      modelPlaceholder="e.g. sarvam-1, eleven_multilingual_v2"
    />
  );
}
