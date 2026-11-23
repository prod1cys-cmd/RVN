% Рисунок: спектр сигнала SYSREF при периодическом и пакетном режимах
Fs = 2.4e9; T = 1/3.125e6; tw = 0.5*T; N = round(40e-6*Fs); t = (0:N-1)/Fs;
per = double(mod(t,T) < tw);                 % периодический SYSREF
bur = per .* (t < 4*T);                      % пакет из 4 импульсов
w = 0.5-0.5*cos(2*pi*(0:N-1)/N);
P = @(x) 20*log10(abs(fft((x-mean(x)).*w))/sum(w)*2+1e-9);
f = (0:N-1)*Fs/N/1e6; k = f<=200; Pp = P(per); Pb = P(bur);
h = fig_new(16,10);
subplot(2,1,1); hold on; box on; grid on;
patch([50 70 70 50],[-140 -140 0 0],[1 0.9 0.7],'EdgeColor','none');
patch([156 165 165 156],[-140 -140 0 0],[1 0.85 0.85],'EdgeColor','none');
plot(f(k), Pp(k), 'r'); ylim([-140 0]); xlim([0 200]); ylabel('дБ'); title('Периодический SYSREF 3,125 МГц: непрерывный линейчатый спектр');
subplot(2,1,2); hold on; box on; grid on;
patch([50 70 70 50],[-140 -140 0 0],[1 0.9 0.7],'EdgeColor','none');
patch([156 165 165 156],[-140 -140 0 0],[1 0.85 0.85],'EdgeColor','none');
plot(f(k), Pb(k), 'b'); ylim([-140 0]); xlim([0 200]); ylabel('дБ'); xlabel('Частота, МГц');
title('Пакет из 4 импульсов в окне 40 мкс: энергия однократного переходного процесса');
fig_save(h,'f20_sysref');
