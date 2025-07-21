import React from 'react';
import ThemeSwitcher from './ThemeSwitcher';
import LanguageSwitcher from './LanguageSwitcher';
import LogoutButton from './LogoutButton';
import { useAuthStore } from '../store/authStore';

const HeaderBar: React.FC = () => {
  const user = useAuthStore((s) => s.user);
  return (
    <div style={{ display: 'flex', alignItems: 'center', height: 56, padding: '0 24px', background: '#fff', borderBottom: '1px solid #eee' }}>
      <div style={{ fontWeight: 700, fontSize: 20, flex: 1 }}>ConvoSphere</div>
      <ThemeSwitcher />
      <LanguageSwitcher />
      {user && <span style={{ margin: '0 16px', fontWeight: 500 }}>{user.username}</span>}
      <LogoutButton />
    </div>
  );
};

export default HeaderBar; 