import ProviderSettings from '@/components/ProviderSettings';

const PROVIDERS = ['OPENAI', 'ANTHROPIC', 'GROQ'];

export default function LLMProviderPage() {
  return (
    <ProviderSettings 
      titlePrefix="LLM"
      titleHighlight="Providers"
      description="Configure your API keys and models for Large Language Models securely."
      providers={PROVIDERS}
      theme="main"
      modelPlaceholder="e.g. gpt-4o, claude-3-5-sonnet"
    />
  );
}
