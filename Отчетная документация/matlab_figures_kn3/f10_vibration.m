% Рисунок: предельный коэффициент улучшения СДЦ при вибрации опорного генератора
G = 1e-9; f = 2:0.1:100;
a = 0.7*ones(size(f)); i1 = f<13.2; a(i1) = 0.001*(2*pi*f(i1)).^2/9.80665;
tau = 100e-6; Ts = [0.33e-3 2e-3]; fg = [3110e6 9470e6];
h = fig_new(16,12);
subplot(2,1,1); hold on; box on; grid on;
cl = {'b','r'}; st = {'-','--'}; leg = {};
for i = 1:2
  for j = 1:2
    A = 4*G*a*fg(i).*abs(sin(pi*f*tau).*sin(pi*f*Ts(j)))./f;
    I = 10*log10(4./A.^2);
    plot(f, I, 'Color', cl{i}, 'LineStyle', st{j});
    leg{end+1} = rus(sprintf('f_{г} = %d МГц, T = %.2f мс', fg(i)/1e6, Ts(j)*1e3));
  end
end
plot([2 100],[47 47],'k:','LineWidth',1.5); leg{end+1} = 'I_{треб} = 47 дБ';
ylim([30 130]); xlabel('Частота вибрации, Гц'); ylabel('I_{пред}, дБ');
legend(leg,'Location','northeast'); title('R = 15 км (\tau = 100 мкс), \Gamma = 10^{-9} 1/g, профиль UR E10');
subplot(2,1,2); hold on; box on; grid on;
fv = 100; beta = G*0.7*9470e6/fv;
fo = (-400:400); L = -120*ones(size(fo));
L(fo==0) = 0; L(abs(fo)==fv) = 20*log10(beta/2); L(abs(fo)==2*fv) = 20*log10(beta^2/8);
stem(fo, L, 'BaseValue', -120, 'Marker', 'none', 'LineWidth', 2);
text(fv+10, 20*log10(beta/2)+5, rus(sprintf('%.1f дБн (\\beta = %.3f рад)', 20*log10(beta/2), beta)));
xlabel('Отстройка от частоты гетеродина 9470 МГц, Гц'); ylabel('Уровень, дБн'); ylim([-120 5]);
title('Боковые составляющие гетеродина при вибрации 0,7 g, 100 Гц');
fig_save(h,'f10_vibration');
A = 4*G*0.7*9470e6*abs(sin(pi*100*100e-6)*sin(pi*100*2e-3))/100; fprintf('X T=2ms: %.1f dB\n',10*log10(4/A^2));
