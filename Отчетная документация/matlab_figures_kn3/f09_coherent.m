% Рисунок: фазирование по копии зондирующего импульса (когерентная обработка на приёме)
randn('seed',3); rand('seed',3);
N = 32; T = 1/1000; lambda = 0.0319;  % X-диапазон
phi0 = 2*pi*rand(1,N);                % случайная начальная фаза магнетрона
v = 6; fd = 2*v/lambda;               % цель 6 м/с
n = 0:N-1;
clut = 10*exp(1i*phi0) .* (1 + 0.03*randn(1,N));          % неподвижная помеха
targ = 0.3*exp(1i*(phi0 + 2*pi*fd*n*T));                 % движущаяся цель
noise = 0.02*(randn(1,N)+1i*randn(1,N));
x = clut + targ + noise;
xc = x.*exp(-1i*phi0);                                     % коррекция по копии
w = 0.54-0.46*cos(2*pi*n/(N-1));
F = @(z) 20*log10(abs(fftshift(fft(z.*w,256)))/sum(w)+1e-6);
fa = (-128:127)/256/T;
h = fig_new(16,12);
subplot(2,2,1); stem(n, mod(phi0,2*pi), 'b','filled','MarkerSize',3); grid on; box on;
xlabel('Номер периода'); ylabel('\phi_0, рад'); title('Фаза копии импульса'); ylim([0 2*pi]);
subplot(2,2,2); hold on; box on; grid on;
plot(n, angle(x), 'ro-','MarkerSize',3); plot(n, angle(xc), 'bs-','MarkerSize',3);
xlabel('Номер периода'); ylabel('Фаза эхо-сигнала, рад'); title('Фаза отсчёта помехи'); ylim([-pi pi]);
legend({'до коррекции','после коррекции'},'Location','southoutside','Orientation','horizontal');
subplot(2,1,2); hold on; box on; grid on;
plot(fa, F(x), 'r'); plot(fa, F(xc), 'b');
plot([fd fd],[-60 25],'k:');
text(fd-10,15,rus(sprintf('цель %d м/с, F_{д} = %.0f Гц',v,fd)),'HorizontalAlignment','right');
xlabel('Доплеровская частота, Гц'); ylabel('Уровень, дБ'); ylim([-60 25]); xlim([-500 500]);
legend({'без фазирования','с фазированием по копии'},'Location','southwest');
title('Доплеровский спектр пачки из 32 импульсов');
fig_save(h,'f09_coherent');
