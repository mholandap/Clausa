import { registerRoot, Composition, AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig } from 'remotion';
import React from 'react';

// Composição de teste no visual do Clausa
const Teste = () => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const s = spring({ frame: f, fps, config: { damping: 12 } });
  return (
    <AbsoluteFill style={{ background: '#0B0B0C', justifyContent: 'center', alignItems: 'center', fontFamily: 'Inter, sans-serif' }}>
      <div style={{ transform: `scale(${0.8 + 0.2 * s})`, opacity: interpolate(f, [0, 10], [0, 1], { extrapolateRight: 'clamp' }),
        color: '#FAFAFA', fontSize: 120, fontWeight: 900, letterSpacing: '-0.04em', textAlign: 'center', lineHeight: 1 }}>
        Remotion<br /><span style={{ background: '#FF8A33', color: '#140A05', padding: '0 12px' }}>funcionando</span>
      </div>
    </AbsoluteFill>
  );
};
const Root = () => <Composition id="Teste" component={Teste} durationInFrames={60} fps={30} width={1080} height={1920} />;
registerRoot(Root);
