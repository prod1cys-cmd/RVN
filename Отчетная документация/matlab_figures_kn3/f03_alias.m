% Рисунок: наложение спектров при вещественной дискретизации 400 МГц
Fs = 400e6; N = 8192; n = 0:N-1; t = n/Fs;
fsig = 60e6; fint = [340e6 455e6];          % помехи в полосах наложения
x = 10^(-6/20)*cos(2*pi*fsig*t) + 10^(-20/20)*cos(2*pi*fint(1)*t) + 10^(-26/20)*cos(2*pi*fint(2)*t);
rng0 = 1; randn('seed',rng0);
x = x + 10^(-70/20)*randn(size(t));
% аналоговый фильтр ПЧ (Баттерворт 4-го порядка, 45–75 МГц) – расчёт АЧХ на частотах помех
f0 = 60e6; Bw = 30e6; nB = 4;
Hb = @(f) 1./sqrt(1+((f.^2-f0^2)./(f*Bw)).^(2*nB));
y = 10^(-6/20)*Hb(fsig)*cos(2*pi*fsig*t) + 10^(-20/20)*Hb(fint(1))*cos(2*pi*fint(1)*t) + 10^(-26/20)*Hb(fint(2))*cos(2*pi*fint(2)*t);
y = y + 10^(-70/20)*randn(size(t));
w = 0.5-0.5*cos(2*pi*n/N); cg = sum(w)/N;
X = 20*log10(abs(fft(x.*w))/N/cg*2+1e-15); Y = 20*log10(abs(fft(y.*w))/N/cg*2+1e-15);
fa = n*Fs/N/1e6; k = 1:N/2;
h = fig_new(16,11);
subplot(2,1,1); hold on; box on; grid on;
patch([50 70 70 50],[-130 -130 5 5],[1 0.9 0.7],'EdgeColor','none');
plot(fa(k), X(k), 'b'); ylim([-130 5]); xlim([0 200]);
title('Без полосового фильтра: помехи 340 и 455 МГц переносятся на 60 и 55 МГц');
ylabel('Уровень, дБпш'); xlabel('Частота после дискретизации, МГц');
subplot(2,1,2); hold on; box on; grid on;
patch([50 70 70 50],[-130 -130 5 5],[1 0.9 0.7],'EdgeColor','none');
plot(fa(k), Y(k), 'b'); ylim([-130 5]); xlim([0 200]);
title(sprintf('С фильтром ПЧ 45–75 МГц (n = 4): ослабление %.0f и %.0f дБ', -20*log10(Hb(fint(1))), -20*log10(Hb(fint(2)))));
ylabel('Уровень, дБпш'); xlabel('Частота после дискретизации, МГц');
fig_save(h,'f03_alias');
